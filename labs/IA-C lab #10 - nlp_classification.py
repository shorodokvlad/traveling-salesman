import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay,
)

CATEGORII = ['sci.space', 'rec.sport.hockey', 'talk.politics.guns', 'comp.graphics']


# ── Date ────────────────────────────────────────────────────────────────────

def incarca_date():
    train = fetch_20newsgroups(
        subset='train', categories=CATEGORII,
        remove=('headers', 'footers', 'quotes'),
    )
    test = fetch_20newsgroups(
        subset='test', categories=CATEGORII,
        remove=('headers', 'footers', 'quotes'),
    )
    return train, test


# ── Pipeline ─────────────────────────────────────────────────────────────────

def construieste_pipeline(clasificator, ngram_range=(1, 1), max_features=None):
    return Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            stop_words='english',
            sublinear_tf=True,       # aplică log(1 + TF) pentru a comprima frecvențele mari
        )),
        ('clf', clasificator),
    ])


def evalueaza_model(pipeline, train, test, verbose=True):
    start = time.time()
    pipeline.fit(train.data, train.target)
    durata = time.time() - start
    pred = pipeline.predict(test.data)
    acc = accuracy_score(test.target, pred)
    if verbose:
        print(f"Acuratețe: {acc:.4f}  |  Timp antrenament: {durata:.2f}s")
        print(classification_report(test.target, pred, target_names=train.target_names))
    return acc, pred, durata


# ── Vizualizare ───────────────────────────────────────────────────────────────

def plot_matrice_confuzie(pred, test, titlu="Matricea de confuzie"):
    cm = confusion_matrix(test.target, pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=test.target_names)
    fig, ax = plt.subplots(figsize=(7, 6))
    disp.plot(ax=ax, colorbar=True, cmap='Blues')
    ax.set_title(titlu)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(f"matrice_{titlu[:20].replace(' ', '_')}.png", dpi=150)
    plt.show()


def plot_comparatie(etichete, acurateti, titlu, xlabel):
    fig, ax = plt.subplots(figsize=(8, 5))
    culori = plt.cm.tab10(np.linspace(0, 1, len(etichete)))
    bare = ax.bar(etichete, acurateti, color=culori, edgecolor='black')
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Acuratețe')
    ax.set_xlabel(xlabel)
    ax.set_title(titlu)
    for bar, val in zip(bare, acurateti):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{titlu[:25].replace(' ', '_')}.png", dpi=150)
    plt.show()


# ── Studii ────────────────────────────────────────────────────────────────────

def studiu_clasificatori(train, test):
    print("\n" + "=" * 60)
    print("SARCINA 2 – Compararea clasificatorilor")
    print("=" * 60)
    clasificatori = {
        'Naive Bayes':    MultinomialNB(),
        'LinearSVC':      LinearSVC(max_iter=2000),
        'Reg. Logistică': LogisticRegression(max_iter=1000, solver='saga'),
        'Random Forest':  RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42),
    }
    acurateti, durate, etichete, rezultate = [], [], [], []
    for nume, clf in clasificatori.items():
        print(f"\n--- {nume} ---")
        pipeline = construieste_pipeline(clf)
        acc, pred, durata = evalueaza_model(pipeline, train, test)
        rezultate.append((acc, pred, nume))
        acurateti.append(acc)
        durate.append(durata)
        etichete.append(nume)
    print("\n" + "-" * 50)
    print(f"{'Clasificator':<22} {'Acuratețe':>10} {'Timp (s)':>10}")
    print("-" * 50)
    for nume, acc, dur in zip(etichete, acurateti, durate):
        print(f"{nume:<22} {acc:>10.4f} {dur:>10.2f}")
    print("-" * 50)
    cel_mai_bun = max(rezultate, key=lambda x: x[0])
    print(f"\nCel mai bun: {cel_mai_bun[2]} (acc={cel_mai_bun[0]:.4f})")
    plot_matrice_confuzie(cel_mai_bun[1], test,
                          f"{cel_mai_bun[2]} – Matrice de confuzie")
    plot_comparatie(etichete, acurateti, "Compararea clasificatorilor", "Clasificator")


def studiu_ngram(train, test):
    print("\n" + "=" * 60)
    print("SARCINA 3 – Variația ngram_range")
    print("=" * 60)
    ngram_configs = [(1, 1), (1, 2), (2, 2), (1, 3)]
    acurateti, etichete = [], []
    for ng in ngram_configs:
        pipeline = construieste_pipeline(LinearSVC(max_iter=2000), ngram_range=ng)
        print(f"\nngram_range = {ng}")
        acc, _, _ = evalueaza_model(pipeline, train, test)
        acurateti.append(acc)
        etichete.append(str(ng))
    plot_comparatie(etichete, acurateti, "Influența ngram_range (SVM)", "ngram_range")


def studiu_max_features(train, test):
    print("\n" + "=" * 60)
    print("SARCINA 4 – Variația max_features")
    print("=" * 60)
    valori = [100, 500, 1000, 5000, 10000, None]
    acurateti, etichete = [], []
    for mf in valori:
        pipeline = construieste_pipeline(LinearSVC(max_iter=2000), max_features=mf)
        label = str(mf) if mf is not None else 'toate'
        print(f"\nmax_features = {label}")
        acc, _, _ = evalueaza_model(pipeline, train, test)
        acurateti.append(acc)
        etichete.append(label)
    plot_comparatie(etichete, acurateti, "Influența max_features (SVM)", "max_features")


def studiu_grid(train, test):
    print("\n" + "=" * 60)
    print("SARCINA 5 (opțional) – Grid ngram × max_features")
    print("=" * 60)
    try:
        import seaborn as sns
    except ImportError:
        print("Instalați seaborn: pip install seaborn")
        return
    ngrams = [(1, 1), (1, 2), (1, 3)]
    features = [500, 2000, 5000, 10000]
    rezultate = np.zeros((len(ngrams), len(features)))
    for i, ng in enumerate(ngrams):
        for j, mf in enumerate(features):
            pipeline = construieste_pipeline(
                LinearSVC(max_iter=2000), ngram_range=ng, max_features=mf
            )
            acc, _, _ = evalueaza_model(pipeline, train, test, verbose=False)
            rezultate[i, j] = acc
            print(f"  ngram={ng}, max_features={mf}: acc={acc:.4f}")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(rezultate, annot=True, fmt='.3f', cmap='YlOrRd',
                xticklabels=features,
                yticklabels=[str(ng) for ng in ngrams], ax=ax)
    ax.set_xlabel('max_features')
    ax.set_ylabel('ngram_range')
    ax.set_title('Acuratețe (SVM) – Grid ngram × max_features')
    plt.tight_layout()
    plt.savefig('grid_ngram_features.png', dpi=150)
    plt.show()


# ── Punct de intrare ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Se încarcă datele 20 Newsgroups...")
    train, test = incarca_date()
    print(f"Train: {len(train.data)} documente | Test: {len(test.data)} documente")

    print("\n" + "=" * 60)
    print("SARCINA 1 – Clasificare de bază (Naive Bayes)")
    print("=" * 60)
    pipeline_baza = construieste_pipeline(MultinomialNB())
    acc, pred, _ = evalueaza_model(pipeline_baza, train, test)
    plot_matrice_confuzie(pred, test, "Naive Bayes – Matrice de confuzie")

    studiu_clasificatori(train, test)
    studiu_ngram(train, test)
    studiu_max_features(train, test)
    studiu_grid(train, test)
