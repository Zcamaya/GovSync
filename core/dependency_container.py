from dataclasses import dataclass

from core.logger import configure_logger
from core.settings import Settings, load_settings
from repositories.account_repository import AccountRepository
from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from services.auth_service import AuthService
from services.history_service import HistoryService
from services.payroll_service import PayrollService
from services.philhealth_service import PhilHealthService
from services.sss_service import SSSService
from services.hdmf_service import HDMFService
from services.statistics_service import StatisticsService
from services.employee_records_service import EmployeeRecordsService
from controllers.payroll_controller import PayrollController
from controllers.sss_controller import SSSController
from controllers.hdmf_controller import HDMFController
from controllers.philhealth_controller import PhilHealthController
from controllers.auth_controller import AuthController
from controllers.employee_records_controller import EmployeeRecordsController


@dataclass
class DependencyContainer:
    settings: Settings
    logger: object
    account_repository: AccountRepository
    history_repository: HistoryRepository
    statistics_repository: StatisticsRepository
    auth_service: AuthService
    history_service: HistoryService
    statistics_service: StatisticsService
    payroll_service: PayrollService
    sss_service: SSSService
    hdmf_service: HDMFService
    payroll_controller: PayrollController
    sss_controller: SSSController
    hdmf_controller: HDMFController
    philhealth_service: PhilHealthService
    philhealth_controller: PhilHealthController
    employee_records_service: EmployeeRecordsService
    employee_records_controller: EmployeeRecordsController
    auth_controller: AuthController


def build_container() -> DependencyContainer:
    settings = load_settings()
    logger = configure_logger(log_dir=settings.log_dir)
    account_repository = AccountRepository(settings.database_path)
    history_repository = HistoryRepository(settings.database_path)
    statistics_repository = StatisticsRepository(settings.database_path)
    auth_service = AuthService(account_repository)
    history_service = HistoryService(history_repository)
    statistics_service = StatisticsService(statistics_repository)
    payroll_service = PayrollService()
    sss_service = SSSService()
    hdmf_service = HDMFService()
    payroll_controller = PayrollController(payroll_service)
    sss_controller = SSSController(sss_service)
    hdmf_controller = HDMFController(hdmf_service)
    philhealth_service = PhilHealthService(history_repository, statistics_repository)
    philhealth_controller = PhilHealthController(philhealth_service)
    employee_records_service = EmployeeRecordsService()
    employee_records_controller = EmployeeRecordsController(employee_records_service)
    auth_controller = AuthController(auth_service)
    return DependencyContainer(
        settings=settings,
        logger=logger,
        account_repository=account_repository,
        history_repository=history_repository,
        statistics_repository=statistics_repository,
        auth_service=auth_service,
        history_service=history_service,
        statistics_service=statistics_service,
        payroll_service=payroll_service,
        sss_service=sss_service,
        hdmf_service=hdmf_service,
        payroll_controller=payroll_controller,
        sss_controller=sss_controller,
        hdmf_controller=hdmf_controller,
        philhealth_service=philhealth_service,
        philhealth_controller=philhealth_controller,
        employee_records_service=employee_records_service,
        employee_records_controller=employee_records_controller,
        auth_controller=auth_controller,
    )
