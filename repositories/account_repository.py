from pathlib import Path

from models.account import Account
from storage.sqlite import connect, initialize_database


class AccountRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def get_by_username(self, username: str) -> Account | None:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT * FROM accounts WHERE username = ?",
                (username,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return Account(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            sss_number=row["sss_number"],
            philhealth_number=row["philhealth_number"],
            hdmf_number=row["hdmf_number"],
            employer_name=row["employer_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_all(self) -> list[Account]:
        connection = connect(self.database_path)
        try:
            rows = connection.execute(
                "SELECT * FROM accounts ORDER BY username COLLATE NOCASE"
            ).fetchall()
        finally:
            connection.close()
        accounts: list[Account] = []
        for row in rows:
            accounts.append(
                Account(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    sss_number=row["sss_number"],
                    philhealth_number=row["philhealth_number"],
                    hdmf_number=row["hdmf_number"],
                    employer_name=row["employer_name"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return accounts

    def delete_by_username(self, username: str) -> None:
        connection = connect(self.database_path)
        try:
            connection.execute(
                "DELETE FROM accounts WHERE username = ?",
                (username,),
            )
            connection.commit()
        finally:
            connection.close()

    def replace_all(self, accounts: list[Account]) -> None:
        connection = connect(self.database_path)
        try:
            connection.execute("DELETE FROM accounts")
            connection.executemany(
                """
                INSERT INTO accounts (username, password_hash, sss_number, philhealth_number, hdmf_number, employer_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        account.username,
                        account.password_hash,
                        account.sss_number,
                        account.philhealth_number,
                        account.hdmf_number,
                        account.employer_name,
                    )
                    for account in accounts
                ],
            )
            connection.commit()
        finally:
            connection.close()

    def save(self, account: Account) -> Account:
        connection = connect(self.database_path)
        try:
            connection.execute(
                """
                INSERT INTO accounts (username, password_hash, sss_number, philhealth_number, hdmf_number, employer_name)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    sss_number = excluded.sss_number,
                    philhealth_number = excluded.philhealth_number,
                    hdmf_number = excluded.hdmf_number,
                    employer_name = excluded.employer_name,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    account.username,
                    account.password_hash,
                    account.sss_number,
                    account.philhealth_number,
                    account.hdmf_number,
                    account.employer_name,
                ),
            )
            connection.commit()
        finally:
            connection.close()
        return self.get_by_username(account.username) or account
