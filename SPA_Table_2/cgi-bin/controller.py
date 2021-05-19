import cgi
import html
import model
import template

def get_form_values():
    form = cgi.FieldStorage()
    form_values = {}
    for name in form:
        form_values[name] = form.getfirst(name)
    return form_values

def get_db_query(form_values):
    cnx = model.establish_connection()
    model.use_database(cnx)
    model.create_table(cnx)
    query = model.get_query(cnx, form_values)
    cnx.close()
    return query

def get_table(query):
    table = []
    for record in query:   
        row = """
            <tr align="center">
              <td>{date}</td>
              <td>{title}</td>
              <td>{quantity}</td>
              <td>{distance}</td>
            </tr>
            """.format(date=record[0], title=record[1], quantity=record[2], distance=record[3])
        table.append(row)
    return ''.join(table)

def main():
    form_values = get_form_values()
    query = get_db_query(form_values)
    table = get_table(query)
    template.get_template(table)

if __name__ == "__main__":
    main()