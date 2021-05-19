
def get_template(table):
    print("Content-type: text/html")
    print()

    pattern = '''
    <html>
      <head>
        <meta charset="UTF-8">
          <title>Homepage Table</title>
          <style>
           select {{
            width: 175px; 
           }}
           input {{
            width: 175px; 
           }}
           td {{
            width: 175px;

           }}
          </style>
      </head>
      <body>
        <h1>Homepage Table</h1>
        <form action="/cgi-bin/controller.py">
          <table border="1" >
            <tr>
              <td>sort by column</td>
              <td>
                <select name="sorted_column">
                  <option>title</option>
                  <option>quantity</option>
                  <option>distance</option>
                </select>
              </td>
              <td>
            <select name="sorting_direction">
              <option>decreasing</option>
              <option>increasing</option>
            </select>
              </td>
            </tr>
          </table>
          <p>
            <select name="selected_column">
              <option>choose column</option>
              <option>title</option>
              <option>quantity</option>
              <option>distance</option>
            </select>
            <select name="selected_condition">
              <option>choose condition</option>
              <option>=</option>
              <option>contains</option>
              <option>></option>
              <option><</option>
            </select>
          <input type="text" name="filtration_value" value="enter value">
          <input type="submit">
          </p>
        </form>
        <table border="1", bordercolor="black" >
          <tr>
            <th>date</th>
            <th>title</th>
            <th>quantity</th>
            <th>distance</th>
          </tr>

            {table}

        </table>
      </body>
    </html>
    '''.format(table=table)
    
    print(pattern)