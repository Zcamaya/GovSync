from repositories.employee_records_repository import EmployeeRecordsRepository

repo = EmployeeRecordsRepository()
opts = repo.get_filter_options(None)
print('clients_count=', len(opts.get('clients', [])))
print('clients_sample=', opts.get('clients', [])[:20])
rows, total = repo.list_employees(None, page=1, page_size=20)
print('rows_len=', len(rows), 'total_count=', total)
for i, r in enumerate(rows[:20], 1):
    print(i, r.get('client'), r.get('philhealth_number'), r.get('lastname'), r.get('birthdate'))
