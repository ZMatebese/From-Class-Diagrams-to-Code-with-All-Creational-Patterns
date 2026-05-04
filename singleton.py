"""
Creational Pattern 6: Singleton
=====================================
Pattern: Singleton
Use Case: Ensure only one instance of the database connection exists globally,
           preventing multiple connections that could exhaust the connection pool
           or cause data inconsistency.

RPL Context:
  The RPL system connects to a central PostgreSQL database. A Singleton
  DatabaseConnection ensures that every part of the system (application
  submission, assessor review, panel decisions) reuses the same connection
  pool rather than opening new connections each time.

  Thread-safe implementation using a lock prevents race conditions during
  concurrent request processing.
"""
import threading
from datetime import datetime
from typing import Optional


class DatabaseConnection:
    """
    Singleton: ensures only one database connection instance exists.
    Thread-safe via a double-checked locking mechanism.
    """

    _instance: Optional["DatabaseConnection"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, host: str = "localhost", port: int = 5432,
                database: str = "rpl_db", user: str = "rpl_admin"):
        """
        Thread-safe Singleton instantiation using double-checked locking.
        The first check avoids acquiring the lock on every call.
        The second check inside the lock prevents race conditions.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:          # double-checked locking
                    instance = super().__new__(cls)
                    instance._initialise(host, port, database, user)
                    cls._instance = instance
        return cls._instance

    def _initialise(self, host: str, port: int, database: str, user: str) -> None:
        """Called only once when the singleton is first created."""
        self.__host = host
        self.__port = port
        self.__database = database
        self.__user = user
        self.__connected = False
        self.__connection_time: Optional[datetime] = None
        self.__query_count: int = 0

    @property
    def host(self): return self.__host
    @property
    def port(self): return self.__port
    @property
    def database(self): return self.__database
    @property
    def is_connected(self): return self.__connected
    @property
    def query_count(self): return self.__query_count
    @property
    def connection_time(self): return self.__connection_time

    def connect(self) -> bool:
        """Simulate opening the database connection."""
        if not self.__connected:
            self.__connected = True
            self.__connection_time = datetime.now()
            print(f"[DB] Connected to {self.__database} at {self.__host}:{self.__port}")
        return True

    def disconnect(self) -> None:
        """Simulate closing the database connection."""
        if self.__connected:
            self.__connected = False
            print(f"[DB] Disconnected from {self.__database}")

    def execute_query(self, query: str) -> dict:
        """Simulate executing a database query."""
        if not self.__connected:
            raise ConnectionError("No active database connection. Call connect() first.")
        self.__query_count += 1
        return {
            "query": query,
            "result": f"Simulated result for query #{self.__query_count}",
            "executed_at": str(datetime.now()),
        }

    def get_connection_info(self) -> dict:
        return {
            "host": self.__host,
            "port": self.__port,
            "database": self.__database,
            "user": self.__user,
            "is_connected": self.__connected,
            "connection_time": str(self.__connection_time),
            "query_count": self.__query_count,
        }

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton (for testing only).
        Should NEVER be called in production code.
        """
        with cls._lock:
            cls._instance = None

    def __repr__(self):
        return (f"DatabaseConnection(host={self.__host}, db={self.__database}, "
                f"connected={self.__connected})")


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Singleton Pattern Demo ===\n")

    # First connection
    db1 = DatabaseConnection(host="db.rpl.ac.za", database="rpl_production")
    db1.connect()
    print(f"db1 id: {id(db1)}")

    # Second call — returns same instance
    db2 = DatabaseConnection()
    print(f"db2 id: {id(db2)}")
    print(f"Same instance? {db1 is db2}")   # Expected: True

    # Execute queries through both references
    result = db1.execute_query("SELECT * FROM rpl_applications WHERE status='Pending'")
    print(f"\nQuery result: {result['result']}")

    db2.execute_query("SELECT * FROM students WHERE student_id='STU-001'")
    print(f"Total queries across all references: {db2.query_count}")  # Should be 2

    # Thread safety demonstration
    print("\n-- Thread safety test --")
    instances = []

    def get_instance():
        conn = DatabaseConnection()
        instances.append(id(conn))

    threads = [threading.Thread(target=get_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique_ids = set(instances)
    print(f"Threads: 10 | Unique instances created: {len(unique_ids)}")
    print(f"All threads got the same instance? {len(unique_ids) == 1}")  # Expected: True
