import os
from tablib import Dataset
import pandas
import pygal
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename


# uploads folder should be exesit
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'CSV','csv'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = f'_5#y2L"F4Q8z\n\xec]/'

file_name = ""
dataset = Dataset()


@app.route('/')
def hello():
    return render_template('home.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    global file_name
    if request.method == 'POST':
        # check if the post request has the file part
        if 'inputFile' not in request.files:
            flash('No file part')
            # print("Not inputFile")
            return redirect(request.url)
        file = request.files['inputFile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            # print("Not selected")
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(filename)))
            file_name = os.path.join(
                app.config['UPLOAD_FOLDER'], str(filename))

            return redirect("show")

        else:
            flash("That file don't allow to use ")
    return render_template("home.html")


@app.route("/show")
def show():
    global header
    global data
    global option
    if file_name == "":
        return redirect("/")
    else:
        with open(file_name, "r") as line:
            dataset.csv = line.read()
        data = dataset.html
        option = ["mean","sum","max","min","count","median","std","var"]
        header = open(file_name).readline().rstrip()
        print(header)
        if "," in header:
        	header = open(file_name).readline().rstrip().split(",")
        elif " " in header:
        	header = open(file_name).readline().rstrip().split(" ")
        elif "." in header:
        	header = open(file_name).readline().rstrip().split(".")
        else:
        	flash("that header of file not support split ")
        	return redirect("/")

        return render_template("show.html", lines=data, option=option, header=header)


@app.route("/analyze")
def analyze():
    name = request.args.get("myselect")
    option_var = request.args.get("myoption")

    if name not in header:
        flash("please select the header and option")
        return redirect("/")
    elif option_var not in option:
        flash("option not found ")
        return redirect("/")

    df = pandas.read_csv(file_name)
    try:
        if option_var == "mean":
            set_data = df[name].mean()
        elif option_var == "sum":
            set_data = df[name].sum()
        elif option_var == "max":
            set_data = df[name].max()
        elif option_var == "count":
            set_data = df[name].count()
        elif option_var == "std":
            set_data = df[name].std()
        elif option_var == "var":
            set_data = df[name].var()
        elif option_var == "min":
            set_data = df[name].min()
    except:
        flash("pleas make sure use the option with the valid header you can't use some option with string value !")
        return redirect("/")

    imported_data = Dataset().load(open(file_name).read())
    data = imported_data[name]
    new_list = []
    for d in data:
        try:
            if d.isdigit():
                new_list.append(int(d))
            elif type(d) == str:
                new_list.append(float(d))
        except:
            flash("this option only for Number")
            return redirect("/")

    graph = pygal.Line()
    graph.title = "Full customization option For " + str(name)
    graph.x_labels = []
    graph.add(name, new_list)
    graph_data = graph.render_data_uri()

    return render_template("analyze.html", set_data=set_data, option_var=option_var, name=name, graph_data=graph_data)


if __name__ == "__main__":
    app.run(debug=False)
