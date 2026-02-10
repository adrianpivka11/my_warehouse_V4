"""my.Warehouse

Warehouse system connected to PostgreSQL.

(learning project)

Note: DB access data is currently directly in the code.
"""

from __future__ import annotations

from audit_log import Audit
from analytics import Analytics
from export_data import ExportData
from auxiliary_functions import _read_int, _read_bool, _read_float

import sys
from typing import Any, Optional

import psycopg
from psycopg import sql



DB_NAME = "Moj_sklad.DB"
DB_USER = "postgres"
DB_PASSWORD = "0123"
DB_HOST = "localhost"
DB_PORT = 5432


# ------------------------------
# Hlavná trieda (API pre CLI)
# ------------------------------

class Warehouse:
    """
    
    Main class of the warehouse system. Calls all the methods from other modules.
    
    """

    allowed_cols = {
        "productname",
        "supplierid",
        "categoryid",
        "quantityperunit",
        "unitprice",
        "unitsinstock",
        "unitsonorder",
        "reorderlevel",
        "discontinued",
    }

    def __init__(self) -> None:
        self.log = Audit()
        self.conn = psycopg.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        self.analytika = Analytics(self.conn, self.log)
        self.export = ExportData(self.conn, self.log)

    def exit_program(self) -> None:
        """Exit program (export log and stop program running)."""
        print("Application has stopped running")
        self.log.write_log("[SHUTDOWN] Application has stopped running")
        self.log.export_log_txt()
        sys.exit(0)

    def print_product_list2(self) -> None:
        """Print basic product list of products."""
        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT productid, productname, unitprice FROM products;")
            for row in cur.fetchall():
                print(row["productid"], row["productname"], row["unitprice"])
        self.log.write_log("[REPORT] Printed basic product list of products")

    def get_product_field(self, column: str, product_id: Any) -> Any:
        """Returns value of chosen column."""
        if column not in self.allowed_cols:
            raise ValueError(f"Column not allowed: {column}")

        with self.conn.cursor() as cur:
            query = sql.SQL("SELECT {col} FROM products WHERE productid = %s").format(
                col=sql.Identifier(column)
            )
            cur.execute(query, (product_id,))
            row = cur.fetchone()
        return row[0] if row else None

    def _list_suppliers(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT supplierid, companyname FROM suppliers;")
            for row in cur.fetchall():
                print(row)

    def _list_categories(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT categoryid, categoryname FROM categories;")
            for row in cur.fetchall():
                print(row)

    def get_supplierid(self) -> int:
        """Let user to choose supplierid."""
        self._list_suppliers()
        return _read_int("\nChoose supplier id: ")

    def get_categoryid(self) -> int:
        """Let user to choose categoryid."""
        self._list_categories()
        return _read_int("\nChoose category id: ")

    def get_discontinued(self) -> bool:
        """Loads discontinued (True/False)."""
        return _read_bool("Is this product discontinued? (y/N): ")

    def add_product2(self) -> None:
        """Adds new product into DB."""
        new_productname = input("Enter product name: ").strip()
        new_supplierid = self.get_supplierid()
        new_categoryid = self.get_categoryid()
        new_quantityperunit = input("Enter quantity per unit: ").strip()
        new_unitprice = _read_float("Enter the unit price of the product: ")
        new_unitsinstock = _read_int("Enter quantity in stock: ")
        new_unitsonorder = _read_int("Enter the ordered quantity: ")
        new_reorderlevel = _read_int("Enter reorder level: ")
        new_discontinued = self.get_discontinued()

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (
                    productname, supplierid, categoryid, quantityperunit,
                    unitprice, unitsinstock, unitsonorder, reorderlevel, discontinued
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING productid;
                """,
                (
                    new_productname,
                    new_supplierid,
                    new_categoryid,
                    new_quantityperunit,
                    new_unitprice,
                    new_unitsinstock,
                    new_unitsonorder,
                    new_reorderlevel,
                    new_discontinued,
                ),
            )
            product_id = cur.fetchone()[0]
            self.conn.commit()

        print(f"Product added. ID={product_id}")
        self.log.write_log(f"[ADD] Product added {new_productname} (ID={product_id})")

    def delete_product2(self) -> None:
        """Deletes product by ID."""
        self.print_product_list2()
        product_id = _read_int("Select the product id of the product you want to delete: ")

        with self.conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM products
                WHERE productid = %s
                RETURNING productid, productname;
                """,
                (product_id,),
            )
            deleted = cur.fetchone()
            self.conn.commit()

        if deleted:
            print("Deleted product:", deleted)
            self.log.write_log(f"[DELETE] Product has been removed.: {deleted}")
        else:
            print("Product has not been found.")

    def select_product(self, product_id: Any) -> Optional[tuple[Any, ...]]:
        """returns the entire product row (or None)."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE productid = %s;", (product_id,))
            return cur.fetchone()

    def update_product(self) -> None:
        """Interactive product UPDATE (change of one column)."""
        self.print_product_list2()
        product_id = _read_int("Select the product ID you want to update: ")
        product = self.select_product(product_id)
        if not product:
            print("Product not found.")
            return

        options = [
            "1. Product name",
            "2. Supplier id",
            "3. Category id",
            "4. Quantity per piece",
            "5. Unit price",
            "6. Quantity in stock",
            "7. Ordered quantity",
            "8. Re-order level",
            "9. Discontinued product",
            "0. End product UPDATE",
        ]
        map_choice_to_col = {
            1: "productname",
            2: "supplierid",
            3: "categoryid",
            4: "quantityperunit",
            5: "unitprice",
            6: "unitsinstock",
            7: "unitsonorder",
            8: "reorderlevel",
            9: "discontinued",
        }

        while True:
            print(f"You have choosen product: {product}")
            for line in options:
                print(line)

            choice = _read_int("Select the parameter you want to change: ")
            if choice == 0:
                return

            col = map_choice_to_col.get(choice)
            if not col:
                print("Dialing out of range. Enter 0–9.")
                continue

            actual_value = self.get_product_field(col, product_id)
            updated_value = input(f"Current: {actual_value!r}. New value for {col}: ")

            with self.conn.cursor() as cur:
                q = sql.SQL("UPDATE products SET {col} = %s WHERE productid = %s").format(
                    col=sql.Identifier(col)
                )
                cur.execute(q, (updated_value, product_id))
                self.conn.commit()

            print("UPDATE was successful.")
            self.log.write_log(
                f"[UPDATE] product_id={product_id} col={col} {actual_value!r} -> {updated_value!r}"
            )

            product = self.select_product(product_id)

    def total_price(self) -> float:
        """Backward compatibility: total warehouse value (SQL)."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(unitsinstock * unitprice), 0) FROM products;")
            total = float(cur.fetchone()[0] or 0)
        print(f"Celková hodnota skladu je {total:.2f} Eur")
        self.log.write_log(f"[REPORT] Celková hodnota skladu: {total:.2f} €")
        return total


""" 

Initialization of object of class 

"""

my_warehouse = Warehouse()
