'''
* mysql-base lib
  * Defines serializable query class
  * Functions for stuff like sanitizing data
  * Actually runs queries from query object

classes
read_query
write_row_query
insert_row
edit_table

* TODO: should all references to columns be column definitions
* TODO: have to be very careful with joins and '.' in fields, else people will
 potentially be able to write into other tabless
* TODO: consider using an abstract base class.
* TODO: replace asserts with raising custom exception type.
'''

from typing import Type, Dict, Tuple, List
#cls: Type[A]

import mysql_query_fragments as frag
from mysql_base import SQLType, get_py_to_sql_cast_func, cast_py_to_sql
from util import *


class ColumnDefinition(object):
    '''Describes a column name, type, and unique constraint'''

    @auto_set_fields
    def __init__(self, name, sql_type, is_unique=False):
        pass

    def to_sql(self):
        return '%s %s' % (self.name, self.sql_type)


class AutoIncrementColumn(ColumnDefinition):
    '''A specific column definition for auto increment columns, intended for IDs.'''

    @auto_set_fields
    def __init__(self, name: str):
        self.sql_type = 'BIGINT'# TODO: figure out if this should be INT or BIGINT
        self.is_unique = False

    def to_sql(self):
        return '%s %s unsigned NOT NULL AUTO_INCREMENT' % (self.name, self.sql_type)


class QueryCriterion(object):
    cr_types_to_strs = {
        'equals': '=',
        'lt': '<',
        'gt': '>',
    }

    @auto_set_fields
    def __init__(self, constraint_type, field_name, comparison_value):
        assert self.constraint_type in list(self.cr_types_to_strs.keys()), "Invalid constraint type."

    def to_sql(self):
        return "%s %s %s" % (self.field_name,
                             self.cr_types_to_strs[self.constraint_type],
                             cast_py_to_sql(self.comparison_value),
                            )


# TODO: Criteria conjuntion class, should be in class hierarchy with QueryCriterion, probably as a child

# Function shared between InsertRows and SelectRows
def format_where_clause(crit):
    if crit:
        return 'WHERE %s' % crit.to_sql()
    else:
        return None


class UpdateRows(object):
    '''
    UPDATE table_name
    SET column1=value, column2=value2,...
    WHERE some_column=some_value
    '''

    @auto_set_fields
    def __init__(self, table_name, criteria, column_value_dict):
        pass

    def to_sql(self):
        # NOTE: We don't enforce caller to have any criteria, i.e. without
        # "WHERE" all rows will be updated, this enforcement should be added
        # In a higher level API to prevent accidental updates of all records.
        assignment_strs = ['%s=%s' % (k, cast_py_to_sql(v)) for (k,v) in self.column_value_dict.items()]


        return intercalate('\n', [
          'UPDATE %s' % self.table_name,
          'SET %s' % intercalate(', ', assignment_strs),
          format_where_clause(self.criteria),
        ])


class InsertRows(object):
    '''
    INSERT INTO table_name
    (column1, column2, column3, ...)
    VALUES
    (value1, value2, value3, ...)
    ;
    '''
    @auto_set_fields
    def __init__(self, table_name, column_names, list_of_values_lists):
        pass

    def to_sql(self):
        correct_len = len(self.column_names)

        for value_list in self.list_of_values_lists:
            assert len(value_list) == correct_len

        casting_funcs = [get_py_to_sql_cast_func(type(x)) for x in self.list_of_values_lists[0]]

        def apply_funcs(xs):
            ''' Apply list of functions over a list of values '''
            return [ f(x) for (f, x) in zip(casting_funcs, xs)]

        def format_values(xs):
            return '(%s)' % ', '.join(xs)

        convert_data_list_to_string = compose(format_values, apply_funcs)
        formatted_values_lists = [convert_data_list_to_string(x) for x in self.list_of_values_lists]

        return '\n'.join([
          'INSERT INTO %s' % self.table_name,
          '(%s)' % ', '.join(self.column_names),
          'VALUES',
          ', '.join(formatted_values_lists),
          ';'
        ])


class SelectRows(object):
    ''' empty list of column names = *
    '''
    '''
    SELECT t1.name, t2.salary FROM employee AS t1, info AS t2
    WHERE t1.name = t2.name;
    '''
    @auto_set_fields
    def __init__(self, table_name, column_names, criteria):
        pass

    @staticmethod
    def format_column_names(c_names):
        if not c_names:
            return '*'
        else:
            return ', '.join(c_names)


    def to_sql(self):
        return intercalate('\n', [
          'SELECT %s' % self.format_column_names(self.column_names),
          'FROM %s' % self.table_name,
          format_where_clause(self.criteria),
        ])


class DescribeTable(object):
    '''

    '''
    pass


class AddTableColumn(object):
    '''
    ALTER TABLE table_name;
    ALTER COLUMN column_name datatype;
    '''
    def __init__(self, **kwargs):
        attrs = [ 'table_name',
                      'column_name',
                      'column_type',
                      'column_is_unique',
        ]

    def to_sql():
        pass


class DropTableColumn(object):
        @auto_set_fields
        def __init__(self, table_name, column_name):
            pass

        def to_sql():
            pass


class DropTable(object):
    '''
    DROP TABLE table_name;
    '''
    @auto_set_fields
    def __init__(self, table_name):
        pass

    def to_sql(self):
        return 'DROP TABLE %s;' % self.table_name


class CreateTable(object):
    ''' Example:
    CREATE TABLE test_users (
    id BIGINT unsigned NOT NULL AUTO_INCREMENT PRIMARY_KEY,
    username VARCHAR(30),
    first_name VARCHAR(30),
    balance BIGINT,
    CONSTRAINT UC_test_users UNIQUE (id,username)
    );
    '''
    @auto_set_fields
    def __init__(self, table_name, primary_key_column_def, other_column_defs):
        pass

    def to_sql(self):
        column_def_strs = (
          [self.primary_key_column_def.to_sql() + ' PRIMARY_KEY'] +
          list(map(lambda x: x.to_sql(), self.other_column_defs))
        )

        unique_column_names = [self.primary_key_column_def.name] + \
          [x.name for x in self.other_column_defs if x.is_unique]

        constraint_sql = 'CONSTRAINT UC_%s UNIQUE (%s)' % \
          (self.table_name, ','.join(unique_column_names))

        table_spec = ',\n'.join(column_def_strs + [constraint_sql])

        return '\n'.join([
          'CREATE TABLE %s (' % self.table_name,
          table_spec,
          ');'
        ])


if __name__ == '__main__':
    print(CreateTable(
      'test_users',
      AutoIncrementColumn('id'),
      [ ColumnDefinition('username', SQLType('VARCHAR', 30), True),
        ColumnDefinition('first_name', SQLType('VARCHAR', 30), False),
        ColumnDefinition('balance', SQLType('BIGINT'), False),
      ]
    ).to_sql())

    print(InsertRows('test_users', ['username', 'first_name', 'balance'],
        [['tester', 'test', 500],
         ['tester2', 'two', 200],
        ]).to_sql())

    print(DropTable('test_users').to_sql())


    print(QueryCriterion('equals', 'username', 'tester').to_sql())

    print(SelectRows('test_users', [], None).to_sql())
    print(SelectRows('test_users', [],
      QueryCriterion('equals', 'username', 'tester')
    ).to_sql())

    print(SelectRows('test_users', [],
      QueryCriterion('gt', 'balance', 10)
    ).to_sql())

    print(SelectRows('test_users', ['username', 'balance'],
      QueryCriterion('gt', 'balance', 10)
    ).to_sql())

    print(UpdateRows('test_users',
      QueryCriterion('equals', 'username', 'tester'),
      {'balance': 0, 'status':'broke'}
    ).to_sql())