from pathlib import Path

from models.account import Account
from storage.sqlite import connect, initialize_database


class AccountRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def get_by_username(self, username: str) -> Account | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return Account(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            sss_number=row["sss_number"],
            philhealth_number=row["philhealth_number"],
            hdmf_number=row["hdmf_number"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_all(self) -> list[Account]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM accounts ORDER BY username COLLATE NOCASE"
            ).fetchall()
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
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return accounts

    def delete_by_username(self, username: str) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                "DELETE FROM accounts WHERE username = ?",
                (username,),
            )
            connection.commit()

    def replace_all(self, accounts: list[Account]) -> None:
        with connect(self.database_path) as connection:
            connection.execute("DELETE FROM accounts")
            connection.executemany(
                """
                INSERT INTO accounts (username, password_hash, sss_number, philhealth_number, hdmf_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        account.username,
                        account.password_hash,
                        account.sss_number,
                        account.philhealth_number,
                        account.hdmf_number,
                    )
                    for account in accounts
                ],
            )
            connection.commit()

    def save(self, account: Account) -> Account:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO accounts (username, password_hash, sss_number, philhealth_number, hdmf_number)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    sss_number = excluded.sss_number,
                    philhealth_number = excluded.philhealth_number,
                    hdmf_number = excluded.hdmf_number,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    account.username,
                    account.password_hash,
                    account.sss_number,
                    account.philhealth_number,
                    account.hdmf_number,
                ),
            )
            connection.commit()
        return self.get_by_username(account.username) or account
