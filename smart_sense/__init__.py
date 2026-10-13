"""
Sweat Sense Django Project Package Initialization.
Registers PyMySQL as MySQLdb for broad environment and serverless compatibility.
"""

try:
    import pymysql
    pymysql.version_info = (2, 2, 8, "final", 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
