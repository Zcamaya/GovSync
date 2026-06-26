from services.sss_engine import (
    TXT_COLUMNS,
    format_employer_id,
    get_default_month_and_year,
    get_months_list,
    get_years_list,
    generate_sss_txt,
    load_sss_txt,
    save_sss_txt,
)


class SSSService:
    def generate_txt(self, progress_callback=None, **kwargs):
        return generate_sss_txt(progress_callback=progress_callback, **kwargs)

    def load_txt(self, file_path):
        return load_sss_txt(file_path)

    def save_txt(self, rows, file_path):
        return save_sss_txt(rows, file_path)


# Re-export SSS helper constants for widget use and cross-component encapsulation.
TXT_COLUMNS = TXT_COLUMNS
format_employer_id = format_employer_id
get_default_month_and_year = get_default_month_and_year
get_months_list = get_months_list
get_years_list = get_years_list
