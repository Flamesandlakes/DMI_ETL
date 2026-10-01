from dmi_etl import DB_operations


def main() -> None:
    print("Hello from dmi-etl!")

    DB_operations.commit_to_postgres()