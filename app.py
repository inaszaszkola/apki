from flask import Flask, render_template, request, session
import random
import re

app = Flask(__name__)
app.secret_key = "gra_luki_fix"

STOP_WORDS = {
    "i", "a", "w", "na", "do", "z", "ze", "że", "to", "jest", "są",
    "się", "o", "u", "by", "był", "była", "było", "ale", "lub", "oraz"
}

def clean(word):
    return re.sub(r"[^\wąćęłńóśźż]", "", word.lower())


def generuj_luki(tekst):
    slowa = tekst.split()

    kandydaci = []
    for i, s in enumerate(slowa):
        czyste = clean(s)
        if len(czyste) >= 5 and czyste not in STOP_WORDS:
            kandydaci.append(i)

    if len(kandydaci) < 3:
        kandydaci = list(range(len(slowa)))

    indeksy = random.sample(kandydaci, min(3, len(kandydaci)))

    # zapis poprawnych odpowiedzi
    odpowiedzi = {str(i): clean(slowa[i]) for i in indeksy}
    session["odpowiedzi"] = odpowiedzi

    for i in indeksy:
        slowa[i] = f"[{i}]_____"

    return " ".join(slowa)


def sprawdz(tekst_user):
    poprawne = session.get("odpowiedzi", {})

    if not poprawne:
        return [], 0, 0

    user = tekst_user.split()

    wynik = []
    punkty = 0

    for i, (idx, good) in enumerate(poprawne.items()):
        try:
            u = clean(user[i])
        except:
            u = ""

        if u == good:
            wynik.append(f"✔ Luka {i+1}: dobrze ({u})")
            punkty += 1
        else:
            wynik.append(f"✖ Luka {i+1}: źle (poprawnie: {good}, ty: {u})")

    return wynik, punkty, len(poprawne)


@app.route("/", methods=["GET", "POST"])
def index():
    wynik = ""
    feedback = []
    score = None

    if request.method == "POST":

        if "tekst" in request.form:
            wynik = generuj_luki(request.form["tekst"])

        if "odpowiedzi" in request.form:
            feedback, p, m = sprawdz(request.form["odpowiedzi"])
            if m > 0:
                score = f"Wynik: {p}/{m} ({int(p/m*100)}%)"

    return render_template("index.html", wynik=wynik, feedback=feedback, score=score)


if __name__ == "__main__":
    app.run(debug=True)