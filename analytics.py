"""
 Analytics (read-only reports)

"""


from audit_log import Audit
import psycopg
from auxiliary_functions import _read_int, _read_float

DB_NAME = "Moj_sklad.DB"
DB_USER = "postgres"
DB_PASSWORD = "0123"
DB_HOST = "localhost"
DB_PORT = 5432




class Analytics:
    """A set of analytical reports over the DB (SQL SELECTs).."""

    def __init__(self, conn: psycopg.Connection, audit: Audit) -> None:
        self.conn = conn
        self.audit = audit
        self.analytics_options = [
            "1. KPI inventory summary (dashboard)",
            "2. Total inventory value (total_value)",
            "3. Value by category",
            "4. Value by supplier",
            "5. TOP / FLOP products by value",
            "6. Low-stock / Out-of-stock report",
            "0. Return to main menu",
        ]

    def display_options(self) -> None:
        """Displays the analytics menu."""
        print("\n")
        for item in self.analytics_options:
            print(item)
        print("\n")


    def user_choice(self) -> int:
        """Loads choice of user."""
        return _read_int("Choose one of the above options: ")

    def my_analytics(self) -> None:
        """Main Loop of analytics menu."""
        while True:
            self.display_options()
            choice = self.user_choice()

            if choice == 0:
                return
            if choice == 1:
                self.get_basic_kpi_dashboard()
            elif choice == 2:
                self.calculate_total_stock_value()
            elif choice == 3:
                self.get_value_by_category()
            elif choice == 4:
                self.get_value_by_supplier()
            elif choice == 5:
                self.get_top_flop_products()
            elif choice == 6:
                self.get_low_stock_report()
            else:
                print("You have entered non-existing option.")

    def calculate_total_stock_value(self) -> float:
        """Calculates and prints the total value of the warehouse."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(unitsinstock * unitprice), 0) FROM products;")
            value = float(cur.fetchone()[0] or 0)
        print(f"The total value of the warehouse: {value:.2f} €")
        self.audit.write_log(f"[ANALYTICS] The total value of the warehouse: {value:.2f} €")
        return value

    def get_basic_kpi_dashboard(self) -> None:
        """Print basic KPIs: numbers, units, value, average price."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(productid) FROM products;")
            products_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(categoryid) FROM categories;")
            category_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(supplierid) FROM suppliers;")
            suppliers_count = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(SUM(unitsinstock), 0) FROM products;")
            total_units = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(ROUND(SUM(unitsinstock * unitprice)), 0) FROM products;")
            total_value = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(ROUND(AVG(unitprice)), 0) FROM products;")
            avg_unitprice = cur.fetchone()[0]

        print(
            "KPIs summary:",
            f"products={products_count}; categories={category_count}; suppliers={suppliers_count};",
            f"total_units={total_units}; total_value={total_value}; avg_unitprice={avg_unitprice}",
        )
        self.audit.write_log("[ANALYTICS] KPI dashboard")

    def get_value_by_category(self) -> None:
        """Report: warehouse value by category"""
        query = (
            "SELECT p.categoryid, c.categoryname, COUNT(productid) AS product_count, "
            "SUM(unitsinstock) AS total_units, ROUND(AVG(unitprice)) AS avg_price, "
            "ROUND(SUM(unitsinstock * unitprice)) AS total_value "
            "FROM products p "
            "JOIN categories c ON p.categoryid = c.categoryid "
            "GROUP BY p.categoryid, c.categoryname "
            "ORDER BY total_value DESC"
        )
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        for r in rows:
            print(
                f"id={r[0]} {r[1]}, product_count={r[2]}, total_units={r[3]}, total_value={r[5]}"
            )
        self.audit.write_log("[ANALYTICS] Value by category")

    def get_value_by_supplier(self) -> None:
        """Report: warehouse value by supplier (with optional limit)."""
        min_value = _read_float(
            "Minimum value of goods in stock from the supplier (0 = no filter): "
        )
        query = (
            "SELECT s.supplierid, s.companyname, COUNT(productid) AS product_count, "
            "SUM(unitsinstock) AS total_units, SUM(unitsinstock * unitprice) AS total_value "
            "FROM suppliers s "
            "LEFT JOIN products p ON s.supplierid = p.supplierid "
            "GROUP BY s.supplierid, s.companyname "
            "HAVING COALESCE(SUM(unitsinstock * unitprice), 0) >= %s "
            "ORDER BY total_value DESC"
        )
        with self.conn.cursor() as cur:
            cur.execute(query, (min_value,))
            rows = cur.fetchall()

        for r in rows:
            print(f"{r[0]} {r[1]}, product_count={r[2]}, total_units={r[3]}, total_value={r[4]}")
        self.audit.write_log("[ANALYTICS] Value by supplier")

    def get_top_flop_products(self) -> None:
        """TOP/FLOP 10 products based on units in stock."""
        choice = _read_int("TOP 10 (1) / FLOP 10 (0): ")
        if choice not in (0, 1):
            print("Enter 1 or 0.")
            return

        order = "DESC" if choice == 1 else "ASC"
        query = (
            "SELECT p.productid, p.productname, s.companyname, p.unitsinstock, "
            "ROUND(p.unitprice) as unitprice, ROUND((p.unitsinstock * p.unitprice), 2) AS stock_value "
            "FROM products p "
            "JOIN suppliers s ON p.supplierid = s.supplierid "
            f"ORDER BY unitsinstock {order} "
            "LIMIT 10;"
        )
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        print("\nproductid - productname - companyname - unitsinstock - unitprice - stock_value")
        for t in rows:
            print(f"{t[0]} {t[1]} {t[2]} {t[3]} {t[4]} {t[5]}")
        self.audit.write_log("[ANALYTICS] Top/Flop products")

    def get_low_stock_report(self) -> None:
        """Report: units, where reorderlevel > unitsinstock."""
        query = (
            "SELECT p.productid, p.productname, s.companyname, c.categoryname, "
            "p.quantityperunit, unitsinstock, unitsonorder, reorderlevel "
            "FROM products p "
            "JOIN suppliers s ON p.supplierid = s.supplierid "
            "JOIN categories c ON p.categoryid = c.categoryid "
            "WHERE reorderlevel > unitsinstock "
            "ORDER BY unitsonorder ASC"
        )
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        print(
            "\nproductid - productname - companyname - categoryname - quantityperunit - "
            "unitsinstock - unitsonorder - reorderlevel"
        )
        for t in rows:
            print(f"{t[0]} {t[1]} {t[2]} {t[3]} {t[4]} {t[5]} {t[6]} {t[7]}")
        self.audit.write_log("[ANALYTICS] Low stock report")

