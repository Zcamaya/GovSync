from widgets.employee_records_panel import sort_payroll_history_for_display


def test_sort_payroll_history_places_latest_month_first():
    history = [
        {"applicable_month": "2024-01", "from_date": "", "to_date": "", "company": "A"},
        {"applicable_month": "2024-03", "from_date": "", "to_date": "", "company": "B"},
        {"applicable_month": "2024-02", "from_date": "", "to_date": "", "company": "C"},
    ]

    sorted_history = sort_payroll_history_for_display(history)

    assert [item["applicable_month"] for item in sorted_history] == ["2024-03", "2024-02", "2024-01"]
