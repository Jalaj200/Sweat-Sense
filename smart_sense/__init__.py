"""
Sweat Sense Django Project Package Initialization.
Registers PyMySQL as MySQLdb for broad environment and serverless compatibility.
"""

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
