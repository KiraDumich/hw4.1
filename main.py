import sqlite3
import flask
import json


def run_sql(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = []
        for item in connection.execute(sql).fetchall():
            result.append(dict(item))

        return result


app = flask.Flask(__name__)


@app.get("/movie/<title>")
def step_1(title):
    sql = f'''select title, country, release_year, listed_in as genre, description from netflix where title='{title}'
    order by date_added desc
    limit 1'''

    return flask.jsonify(run_sql(sql))
    # return app.response_class(json.dumps(result, ensure_ascii=False, indent=8, mimitype="application/json"))


@app.get("/movie/<int:year1>/to/<int:year2>")
def step_2(year1, year2):
    sql = f'''
            select * from netflix
            where release_year between {year1} and {year2}
    '''

    return flask.jsonify(run_sql(sql))


@app.get("/rating/<rating>")
def step_3(rating):
    my_dict = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }
    sql = f'''
            select title, rating, description from netflix
            where rating in {my_dict.get(rating, ('PG-13', 'NC-17'))}
    '''

    return flask.jsonify(run_sql(sql))


@app.get("/genre/<genre>")
def step_4(genre):
    sql = f'''
          select * from netflix
          where listed_in like '{genre.title()}%'
    '''
    return flask.jsonify(run_sql(sql))


@app.get("/movies/<name_1>/and/<name_2>")
def step_5(name_1, name_2):
    sql = f'''
           select * from netflix
           where "cast" like '%{name_1}%' and cast like '%{name_2}%'
           '''
    result = run_sql(sql)
    print(result)

    names = {}
    for item in result:
        names_main = item.get('cast').split(", ")
        for name in names_main:
            if name in names.keys():
                names[name] += 1
            else:
                names[name] = 1

    result = []
    for item in names:
        if item not in (name_1, name_2) and names[item] >= 2:
            result.append(item)

    return result


@app.get("/movies/<types>/<release_year>/<genre>")
def step_6(types='TV Show', release_year=2021, genre='TV'):
    sql = f'''
           select * from netflix
           where type = '{types}'
           and release_year = '{release_year}'
           and listed like '%{genre}%'
        '''
    return flask.jsonify(run_sql(sql))


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
