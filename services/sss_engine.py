import datetime
import os
import re

import pandas as pd


MONTHS = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]

TXT_COLUMNS = [
    "Employer ID",
    "Branch Code",
    "Employee ID",
    "Lastname",
    "Firstname",
    "Suffix",
    "MI",
    "Monthly Salary",
    "Status",
    "Hiring/Separation Date",
    "Position",
]


def get_months_list():
    return MONTHS.copy()


def get_years_list():
    current_year = datetime.date.today().year
    return [str(year) for year in range(current_year, 1956, -1)]


def get_default_month_and_year():
    today = datetime.date.today()
    first_of_this_month = today.replace(day=1)
    previous_month = first_of_this_month - datetime.timedelta(days=1)
    return previous_month.strftime("%B").upper(), previous_month.strftime("%Y")


def format_employer_id(raw_value):
    digits = digits_only(raw_value)[:10]
    formatted = digits[:2]

    if len(digits) > 2:
        formatted += "-" + digits[2:9]
    if len(digits) > 9:
        formatted += "-" + digits[9:10]

    return formatted


def digits_only(value):
    return "".join(re.findall(r"\d", str(value)))


def find_sheet_name(file_path, target_name):
    workbook = pd.ExcelFile(file_path)
    normalized_target = target_name.strip().lower()

    for sheet_name in workbook.sheet_names:
        if sheet_name.strip().lower() == normalized_target:
            return sheet_name

    available = ", ".join(workbook.sheet_names) or "none"
    raise ValueError(f"No '{target_name}' sheet found. Available sheets: {available}")


def load_corrections(correction_file_path):
    corrections = {}
    if not correction_file_path:
        return corrections

    corr_df = pd.read_excel(correction_file_path, header=None, dtype=str)
    for _, row in corr_df.iterrows():
        sss = str(row[0]).strip().split(".")[0].zfill(10)
        corrections[sss] = {
            "LAST": cell_value(row, 2),
            "FIRST": cell_value(row, 3),
            "SUFFIX": cell_value(row, 4),
            "MI": cell_value(row, 5),
        }

    return corrections


def cell_value(row, index):
    return str(row[index]) if pd.notna(row[index]) else "NULL"


def clean_value(value, middle_initial=False):
    if pd.isna(value) or str(value).lower() in ["nan", "none"]:
        return "NULL"

    cleaned = str(value)
    cleaned = cleaned.replace("\u00e2\u2022\u00a4", "\u00d1")
    cleaned = cleaned.replace("\u00e2\u2022\u00a4".lower(), "\u00f1")
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned).strip()

    if not cleaned:
        return "NULL"

    return cleaned[0].upper() if middle_initial else cleaned


def parse_period(month, year):
    user_month_input = f"{month} {year}"

    for date_format in ("%B %Y", "%b %Y", "%B%Y", "%b%Y"):
        try:
            return datetime.datetime.strptime(
                user_month_input.upper(),
                date_format,
            ).date()
        except ValueError:
            continue

    raise ValueError("Invalid month or year.")


def build_column_map(dataframe):
    if len(dataframe.columns) < 5:
        raise ValueError("The SSS sheet must have at least 5 columns.")

    def find_column(*names):
        targets = {name.strip().upper().replace(" ", "") for name in names}
        for column in dataframe.columns:
            normalized = str(column).strip().upper().replace(" ", "")
            if normalized in targets:
                return column
        return None

    salary_column = find_column("BASICRATE", "MONTHLYSALARY", "SALARY")
    if not salary_column:
        fallback_salary = dataframe.columns[4]
        normalized_fallback = str(fallback_salary).strip().upper().replace(" ", "")
        if normalized_fallback in {"BIRTHDATE", "DATEHIRED", "HIRED", "HIRINGDATE"}:
            raise ValueError(
                "The SSS sheet has no monthly salary column. "
                "Run Earnings Automation again so the SSS sheet includes basicrate."
            )
        salary_column = fallback_salary

    column_map = {
        "ID": find_column("SSSNO", "SSS", "ID") or dataframe.columns[0],
        "LAST": find_column("LASTNAME", "LAST") or dataframe.columns[1],
        "FIRST": find_column("FIRSTNAME", "FIRST") or dataframe.columns[2],
        "MID": find_column("MIDDLENAME", "MIDDLE", "MI") or dataframe.columns[3],
        "SALARY": salary_column,
        "SSSREM": find_column("SSSREM"),
        "HIRED": find_column("DATEHIRED", "HIRED", "HIRINGDATE"),
        "POSITION": find_column("POSITION"),
    }
    return column_map


def generate_sss_txt(
    source_file_path,
    output_directory,
    employer_id,
    branch_code,
    month,
    year,
    correction_file_path="",
    progress_callback=None,
):
    if not source_file_path or not output_directory:
        raise ValueError("Please select a valid source file and save folder.")
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Source file cannot be found: {source_file_path}")
    if not os.path.isdir(output_directory):
        raise FileNotFoundError(f"Save folder does not exist: {output_directory}")
    if correction_file_path and not os.path.exists(correction_file_path):
        raise FileNotFoundError(f"Correction file cannot be found: {correction_file_path}")

    employer_digits = digits_only(employer_id)
    if len(employer_digits) != 10:
        raise ValueError("Employer SSS ID must contain exactly 10 digits.")

    branch = branch_code.strip()
    if not branch.isdigit() or len(branch) > 3:
        raise ValueError("Branch code must contain up to 3 digits.")
    branch = branch.zfill(3)

    parsed_target_date = parse_period(month, year)
    start_limit = (parsed_target_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=5)
    end_limit = (parsed_target_date + datetime.timedelta(days=32)).replace(day=1)
    end_limit = end_limit - datetime.timedelta(days=1)
    effective_date = parsed_target_date.replace(day=1).strftime("%m01%Y")

    corrections = load_corrections(correction_file_path)
    sheet_name = find_sheet_name(source_file_path, "SSS")
    dataframe = pd.read_excel(source_file_path, sheet_name=sheet_name, dtype=str)
    dataframe.columns = [str(column).strip().upper() for column in dataframe.columns]
    column_map = build_column_map(dataframe)

    base_name = os.path.splitext(os.path.basename(source_file_path))[0]
    output_path = os.path.join(output_directory, f"{base_name}_PartialListData.txt")
    total_rows = max(len(dataframe), 1)
    written_rows = 0

    with open(output_path, "w", encoding="cp1252", errors="replace") as output_file:
        for index, row in dataframe.iterrows():
            sss_value = str(row[column_map["ID"]]).strip()
            last_name = str(row[column_map["LAST"]]).strip()

            if should_stop(sss_value, last_name):
                break

            line = build_output_line(
                row,
                column_map,
                corrections,
                employer_digits,
                branch,
                start_limit,
                end_limit,
                effective_date,
            )
            output_file.write(line)
            written_rows += 1

            if progress_callback:
                progress_callback(int(((index + 1) / total_rows) * 100))

    if progress_callback:
        progress_callback(100)

    return output_path, written_rows


def should_stop(sss_value, last_name):
    invalid_sss = ["nan", "none", "", "sss", "id", "name"]
    invalid_last = ["nan", "none", "total", "summary", "grand total"]
    return sss_value.lower() in invalid_sss or last_name.lower() in invalid_last


def build_output_line(
    row,
    column_map,
    corrections,
    employer_digits,
    branch,
    start_limit,
    end_limit,
    effective_date,
):
    sss = str(row[column_map["ID"]]).strip().split(".")[0].zfill(10)

    if sss in corrections:
        last_name = corrections[sss]["LAST"]
        first_name = corrections[sss]["FIRST"]
        suffix = corrections[sss]["SUFFIX"]
        middle_initial = corrections[sss]["MI"]
    else:
        last_name = clean_value(row[column_map["LAST"]])
        first_name = clean_value(row[column_map["FIRST"]])
        suffix = "NULL"
        middle_initial = clean_value(row[column_map["MID"]], middle_initial=True)

    salary = parse_salary(row, column_map)

    prefix = (
        f"{employer_digits};{branch};{sss};{last_name};{first_name};"
        f"{suffix};{middle_initial};{salary:.1f};"
    )

    if is_new_employee(row, column_map, start_limit, end_limit):
        position = clean_value(row[column_map["POSITION"]])
        return f"{prefix}1;{effective_date};{position}\n"

    return f"{prefix}N;NULL;NULL\n"


def parse_salary(row, column_map):
    salary = number_value(row[column_map["SALARY"]])
    if salary is not None:
        return salary

    if column_map.get("SSSREM"):
        sss_remittance = number_value(row[column_map["SSSREM"]])
        if sss_remittance is not None:
            return sss_remittance / 0.15

    return 0.0


def number_value(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"} or text.startswith("="):
        return None

    try:
        return float(text.replace(",", ""))
    except (TypeError, ValueError):
        return None


def is_new_employee(row, column_map, start_limit, end_limit):
    if not column_map["HIRED"] or not column_map["POSITION"]:
        return False

    try:
        hired_date = pd.to_datetime(row[column_map["HIRED"]]).date()
    except Exception:
        return False

    return start_limit <= hired_date <= end_limit


def load_sss_txt(file_path):
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"TXT file cannot be found: {file_path}")

    rows = []
    with open(file_path, "r", encoding="cp1252", errors="replace") as input_file:
        for line in input_file:
            line = line.rstrip("\r\n")
            if not line:
                continue

            values = line.split(";")
            if len(values) < len(TXT_COLUMNS):
                values.extend(["NULL"] * (len(TXT_COLUMNS) - len(values)))
            elif len(values) > len(TXT_COLUMNS):
                values = values[: len(TXT_COLUMNS) - 1] + [
                    ";".join(values[len(TXT_COLUMNS) - 1 :])
                ]

            rows.append(dict(zip(TXT_COLUMNS, values)))

    return rows


def save_sss_txt(file_path, rows):
    if not file_path:
        raise ValueError("Please choose a save path.")

    with open(file_path, "w", encoding="cp1252", errors="replace") as output_file:
        for row in rows:
            values = [clean_txt_cell(row.get(column, "NULL")) for column in TXT_COLUMNS]
            output_file.write(";".join(values) + "\n")

    return file_path, len(rows)


def clean_txt_cell(value):
    text = "" if value is None else str(value)
    text = text.replace("\r", " ").replace("\n", " ").strip()
    return text or "NULL"
