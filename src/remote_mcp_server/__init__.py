import json
from fastmcp import FastMCP
import os
import sqlite3

# Use an environment variable for the DB path if provided,
# otherwise default to a local file. This is crucial for deployments
# where the code directory might be read-only.
db_path = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "expense.db"))

mcp=FastMCP("ExpenceTracker")

def init_db():
    with sqlite3.connect(db_path) as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expense(
                id INTEGER PRIMARY KEY  AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT " " ,
                note TEXT DEFAULT " "
            )
            """
        )
        
init_db()

@mcp.tool
def add_expense(date,amount,category,subcategory="",note=""):
    """To add expense to teh expense tracker we use this tool which has varius parameters to add data to the databse and save them"""
    with sqlite3.connect(db_path) as c:
        curr=c.execute("INSERT INTO expense(date,amount,category,subcategory,note) VALUES (?,?,?,?,?)",(date,amount,category,subcategory,note))
        return {"status":"OK all data added","id":curr.lastrowid}

@mcp.tool
def get_expenses():
    """To get expense data from teh expense tracker we use this tool which has varius parameters to get data from the databse """
    with sqlite3.connect(db_path) as c:

        c.row_factory = sqlite3.Row

        rows = c.execute("""
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expense
            ORDER BY date DESC
        """).fetchall()

        return [dict(row) for row in rows]
    
@mcp.tool
def update_expense(
    id,
    date,
    amount,
    category,
    subcategory="",
    note=""
):
    """To update expense in teh expense tracker data we use this tool which has varius parameters to update data to the databse and save them of that particular expense on teh particular id of that expense"""
    with sqlite3.connect(db_path) as c:

        curr = c.execute(
            """
            UPDATE expense
            SET
                date = ?,
                amount = ?,
                category = ?,
                subcategory = ?,
                note = ?
            WHERE id = ?
            """,
            (
                date,
                amount,
                category,
                subcategory,
                note,
                id
            )
        )

        if curr.rowcount == 0:
            return {
                "status": "ERROR",
                "message": "Expense not found"
            }

        return {
            "status": "OK",
            "message": "Expense updated successfully",
            "id": id
        }

@mcp.tool
def delete_expense(id):
    """To delete expense from teh expense tracker we use this tool which has varius parameters to delete data to the databse """
    with sqlite3.connect(db_path) as c:

        curr = c.execute(
            """
            DELETE FROM expense
            WHERE id = ?
            """,
            (id,)
        )

        if curr.rowcount == 0:
            return {
                "status": "ERROR",
                "message": "Expense not found"
            }

        return {
            "status": "OK",
            "message": "Expense deleted successfully",
            "id": id
        }
        
@mcp.tool
def list_expenses(start_date, end_date):
    """List out all the expenses within the range user has asked for """
    with sqlite3.connect(db_path) as c:
        curr = c.execute(
            """
            SELECT id,date,amount,category,subcategory,note FROM expense WHERE date BETWEEN ? AND ? ORDER BY id ASC
            """, (start_date, end_date)
        )
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, r)) for r in curr.fetchall()]
    
@mcp.tool
def summarize(start_date, end_date, category=None):
    """Summerize expense list on teh basis of categiry on the basisi of start_date and end_date"""
    with sqlite3.connect(db_path) as c:
        query = """
            SELECT category, SUM(amount) as TOTAL_AMOUNT 
            FROM expense 
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " GROUP BY category ORDER BY category ASC"
        
        curr = c.execute(query, params)
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, r)) for r in curr.fetchall()]
 
@mcp.tool
def add(a:float,b:float)->int:
    """Addition tool """   
    return a+b

@mcp.resource("info://server")
def server_info()->str:
    """Get the server inforamtion
    """
    info={
        "name":"Simple Expense tracker",
        "version":"1.0.0",
        "author":"test_admin"
    }
    return json.dumps(info,indent=2)

if __name__=="__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)
    
