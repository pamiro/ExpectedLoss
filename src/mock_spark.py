import random
from datetime import date, timedelta
import math

class MockColumn:
    def __init__(self, expr):
        self.expr = expr # Function receiving a row dict and returning a value
        
    def __add__(self, other):
        return self._op(other, lambda a, b: a + b)
    def __sub__(self, other):
        return self._op(other, lambda a, b: a - b)
    def __mul__(self, other):
        return self._op(other, lambda a, b: a * b)
    def __truediv__(self, other):
        return self._op(other, lambda a, b: a / b)
    def __lt__(self, other):
        return self._op(other, lambda a, b: a < b)
    def __le__(self, other):
        return self._op(other, lambda a, b: a <= b)
    def __gt__(self, other):
        return self._op(other, lambda a, b: a > b)
    def __ge__(self, other):
        return self._op(other, lambda a, b: a >= b)
    def __eq__(self, other):
        return self._op(other, lambda a, b: a == b)

    # Reverse operators for 1.0 + col
    def __radd__(self, other):
        return self._op(other, lambda a, b: b + a)
    def __rsub__(self, other):
        return self._op(other, lambda a, b: b - a)
    def __rmul__(self, other):
        return self._op(other, lambda a, b: b * a)
    def __rtruediv__(self, other):
        return self._op(other, lambda a, b: b / a)

    def _op(self, other, func):
        def new_expr(uplink):
            val_self = self.expr(uplink)
            val_other = other.expr(uplink) if isinstance(other, MockColumn) else other
            if val_self is None or val_other is None: return None
            return func(val_self, val_other)
        return MockColumn(new_expr)
    
    def alias(self, name):
        self.name_override = name
        return self
    
    def cast(self, type_str):
        # mock cast
        def new_expr(uplink):
            val = self.expr(uplink)
            if type_str == "int": return int(val) if val is not None else None
            return val
        return MockColumn(new_expr)

class MockFunctions:
    @staticmethod
    def col(name):
        return MockColumn(lambda row: row.get(name))
    
    @staticmethod
    def lit(val):
        return MockColumn(lambda row: val)
    
    @staticmethod
    def when(condition, value):
        # Value can be col or lit
        def new_expr(uplink):
            if condition.expr(uplink):
                return value.expr(uplink) if isinstance(value, MockColumn) else value
            # Need to handle 'otherwise' chain? 
            # Simplified: return None (which acts as default if no otherwise)
            return None 
        
        col = MockColumn(new_expr)
        
        # Add .otherwise method to the column instance
        def otherwise(else_val):
            prev_expr = col.expr
            def otherwise_expr(uplink):
                res = prev_expr(uplink)
                if res is not None: return res
                return else_val.expr(uplink) if isinstance(else_val, MockColumn) else else_val
            return MockColumn(otherwise_expr)
        
        col.otherwise = otherwise
        col.when = lambda c, v: MockFunctions._chained_when(col, c, v)
        return col

    @staticmethod
    def _chained_when(prev_col, condition, value):
        # Support .when().when()
        def new_expr(uplink):
            prev_res = prev_col.expr(uplink)
            if prev_res is not None: return prev_res
            if condition.expr(uplink):
                return value.expr(uplink) if isinstance(value, MockColumn) else value
            return None
        
        col = MockColumn(new_expr)
        col.otherwise = prev_col.otherwise # copy method
        col.when = lambda c, v: MockFunctions._chained_when(col, c, v)
        return col

    @staticmethod
    def rand():
        return MockColumn(lambda row: random.random())
    @staticmethod
    def concat(*cols):
        def new_expr(uplink):
            res = ""
            for c in cols:
                val = c.expr(uplink) if isinstance(c, MockColumn) else c
                res += str(val) if val is not None else ""
            return res
        return MockColumn(new_expr)
    
    @staticmethod
    def date_add(date_col, days_col):
        def new_expr(uplink):
            d = date_col.expr(uplink)
            days = days_col.expr(uplink) if isinstance(days_col, MockColumn) else days_col
            if isinstance(d, str): d = date.fromisoformat(d)
            if d is None: return None
            return d + timedelta(days=int(days))
        return MockColumn(new_expr)
    
    @staticmethod
    def date_sub(date_col, days_col):
        def new_expr(uplink):
            d = date_col.expr(uplink)
            days = days_col.expr(uplink) if isinstance(days_col, MockColumn) else days_col
            if isinstance(d, str): d = date.fromisoformat(d)
            if d is None: return None
            return d - timedelta(days=int(days))
        return MockColumn(new_expr)
        
    @staticmethod
    def expr(sql_expr):
        # Super simplified expr parser for date_add logic used in code
        # "date_add(to_date('2020-01-01'), cast(month_idx * 30 as int))"
        # We'll just hardcode specific patterns or fail
        if "date_add" in sql_expr:
             # Hacky: Assume it's the specific call from data_model
             start_str = sql_expr.split("'")[1]
             start_d = date.fromisoformat(start_str)
             return MockColumn(lambda row: start_d + timedelta(days=int(row.get('month_idx', 0)*30)))
        return MockColumn(lambda row: None)

    @staticmethod
    def sum(col):
        # Aggregation function
        c = col if isinstance(col, MockColumn) else MockFunctions.col(col)
        c.agg_type = 'sum'
        return c
        
    @staticmethod
    def collect_list(col):
        c = col if isinstance(col, MockColumn) else MockFunctions.col(col)
        c.agg_type = 'collect_list'
        return c

    @staticmethod
    def struct(*cols_or_names):
        # Simplified: just return a dict
        def new_expr(uplink):
            res = {}
            for item in cols_or_names:
                if isinstance(item, MockColumn):
                    # Try to guess name?
                    k = getattr(item, 'name_override', 'col')
                    v = item.expr(uplink)
                    res[k] = v
                else: 
                    # Assuming checking existing col
                    res[item] = uplink.get(item)
            return res
        return MockColumn(new_expr)

    @staticmethod
    def pow(base, exponent):
         return MockColumn(lambda row: math.pow(
             base.expr(row) if isinstance(base, MockColumn) else base,
             exponent.expr(row) if isinstance(exponent, MockColumn) else exponent
         ))

class MockDataFrame:
    def __init__(self, data, columns):
        # data is list of dicts or list of rows (if created via createDataFrame with tuple)
        self.data = []
        if data and isinstance(data[0], (list, tuple)):
            for row in data:
                self.data.append(dict(zip(columns, row)))
        elif data and isinstance(data[0], dict):
            self.data = data
        else:
            self.data = []
        self.columns = columns
        
    def withColumn(self, name, col_expr):
        new_data = []
        for row in self.data:
            new_row = row.copy()
            val = col_expr.expr(row)
            new_row[name] = val
            new_data.append(new_row)
        cols = self.columns + [name] if name not in self.columns else self.columns
        return MockDataFrame(new_data, cols)
        
    def withColumnRenamed(self, old_name, new_name):
        new_data = []
        for row in self.data:
            new_row = row.copy()
            if old_name in new_row:
                new_row[new_name] = new_row.pop(old_name)
            new_data.append(new_row)
        new_cols = [new_name if c == old_name else c for c in self.columns]
        return MockDataFrame(new_data, new_cols)
        
    def drop(self, *names):
        new_data = []
        for row in self.data:
            new_row = {k:v for k,v in row.items() if k not in names}
            new_data.append(new_row)
        new_cols = [c for c in self.columns if c not in names]
        return MockDataFrame(new_data, new_cols)
        
    def filter(self, condition):
        new_data = [row for row in self.data if condition.expr(row)]
        return MockDataFrame(new_data, self.columns)
        
    def select(self, *cols):
        # simplistic
        new_data = []
        new_api_cols = []
        for c in cols:
            if isinstance(c, str): new_api_cols.append(c)
            elif isinstance(c, MockColumn): 
                # name?
                name = getattr(c, 'name_override', 'col')
                new_api_cols.append(name)
        
        for row in self.data:
            new_row = {}
            for i, c in enumerate(cols):
                if isinstance(c, str):
                    new_row[c] = row.get(c)
                else:
                    name = getattr(c, 'name_override', f'col_{i}')
                    new_row[name] = c.expr(row)
            new_data.append(new_row)
        return MockDataFrame(new_data, new_api_cols)
    
    def crossJoin(self, other):
        joined = []
        new_cols = self.columns + [c for c in other.columns if c not in self.columns]
        for r1 in self.data:
            for r2 in other.data:
                # Merge dicts
                new_r = r1.copy()
                new_r.update(r2)
                joined.append(new_r)
        return MockDataFrame(joined, new_cols)
        
    def join(self, other, on, how='inner'):
        # Only support simple equi-join on list of keys
        if isinstance(on, str): on = [on]
        joined = []
        other_map = {tuple(r[k] for k in on): r for r in other.data}
        
        # New columns: self + (other - on)
        other_cols = [c for c in other.columns if c not in on]
        new_cols = self.columns + other_cols
        
        for r1 in self.data:
            key = tuple(r1[k] for k in on)
            if key in other_map:
                r2 = other_map[key]
                new_r = r1.copy()
                # add other cols
                for oc in other_cols:
                    new_r[oc] = r2.get(oc)
                joined.append(new_r)
        return MockDataFrame(joined, new_cols)
        
    def groupBy(self, *cols):
        return MockGroupedData(self.data, cols)
        
    def count(self):
        return len(self.data)
        
    def collect(self):
        # Return list of Row-like objects
        # We'll just return dicts for now but code expects .attribute access sometimes
        # Let's wrap in a simple class
        class Row(dict):
            def __getattr__(self, item):
                return self.get(item)
            def __getitem__(self, item):
                return self.get(item)
        return [Row(r) for r in self.data]
        
    def cache(self):
        return self
    
    def orderBy(self, *cols):
        # Sort data
        # assumption: cols are strings
        sorted_data = sorted(self.data, key=lambda r: tuple(r.get(c) for c in cols))
        return MockDataFrame(sorted_data, self.columns)

class MockGroupedData:
    def __init__(self, data, group_cols):
        self.data = data
        self.group_cols = group_cols
        
    def agg(self, *exprs):
        # Group
        groups = {}
        for row in self.data:
            key = tuple(row[k] for k in self.group_cols)
            if key not in groups: groups[key] = []
            groups[key].append(row)
            
        result_data = []
        generated_cols = []
        
        # Identify output columns
        for expr in exprs:
            if isinstance(expr, MockColumn):
                name = getattr(expr, 'name_override', 'agg')
                generated_cols.append(name)
        
        result_cols = list(self.group_cols) + generated_cols
        
        for key, rows in groups.items():
            new_row = dict(zip(self.group_cols, key))
            
            for expr in exprs:
                if isinstance(expr, MockColumn):
                    agg_type = getattr(expr, 'agg_type', None)
                    name = getattr(expr, 'name_override', 'agg')
                    
                    if agg_type == 'sum':
                        # Sum expr over rows
                        val = sum([expr.expr(r) or 0.0 for r in rows])
                        new_row[name] = val
                    elif agg_type == 'collect_list':
                        val = [expr.expr(r) for r in rows]
                        new_row[name] = val
                    else:
                        new_row[name] = None
            result_data.append(new_row)
            
        return MockDataFrame(result_data, result_cols)
        
    def count(self):
        # Not standard pyspark but used in transition matrix logic
        # groupBy(..).count() returns a DF with count col
        groups = {}
        for row in self.data:
            key = tuple(row[k] for k in self.group_cols)
            groups[key] = groups.get(key, 0) + 1
            
        res_data = []
        for key, cnt in groups.items():
            r = dict(zip(self.group_cols, key))
            r['count'] = cnt
            res_data.append(r)
        return MockDataFrame(res_data, list(self.group_cols) + ['count'])

class MockSparkSession:
    class Builder:
        def appName(self, name): return self
        def getOrCreate(self): return MockSparkSession()
    
    builder = Builder()
    
    def __init__(self):
        self.sparkContext = self
        
    def setLogLevel(self, level): pass
    
    def range(self, start, end):
        data = [{'id': i} for i in range(start, end)]
        return MockDataFrame(data, ["id"])
        
    def createDataFrame(self, data, schema=None):
        # Schema can be list of strings or StructType
        cols = []
        if isinstance(schema, list): cols = schema
        elif hasattr(schema, 'names'): cols = schema.names
        
        return MockDataFrame(data, cols)
        
    def stop(self): pass

class MockWindow:
    @staticmethod
    def partitionBy(*cols): return None # Not implemented validation

# Expose as a module
F = MockFunctions
SparkSession = MockSparkSession
Window = MockWindow
