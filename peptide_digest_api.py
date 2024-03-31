from fastapi import FastAPI, HTTPException
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8050"],  # Allow your Dash app's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def retrieve_article(doi=None, url=None):
    """
    Retrieve an article from a SQLite database.

    Parameters
    ----------
    doi : str, optional
        The DOI of the article to be retrieved.
    url : str, optional
        The URL of the article to be retrieved.

    Returns
    -------
    dict
        A dictionary containing the title, authors, journal, date, URL, DOI, and keywords of the article.
    """
    if not doi and not url:
        return "No DOI or URL provided."

    if url and not url.startswith("https://"):
        if url.startswith("www."):
            url = "https://" + url
        else:
            url = "https://www." + url

    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    if doi:
        c.execute("SELECT * FROM articles WHERE doi=?", (doi,))
    elif url:
        c.execute("SELECT * FROM articles WHERE url=?", (url,))
    else:
        return "No DOI or URL provided."
    article = c.fetchone()
    conn.close()

    if article:
        article_info = {
            "title": article[0],
            "authors": article[1],
            "journal": article[2],
            "publisher": article[3],
            "date": article[4],
            "url": article[5],
            "doi": article[6],
            "keywords": article[7],
            "model_bullet_points": article[8],
            "model_summary": article[9],
            "model_metadata": article[10],
            "peptides": article[11],
            "proteins": article[12],
            "model_score": article[13],
            "model_score_justification": article[14],
        }
        return article_info
    else:
        return "Article not found in database."




@app.get("/retrieve/")
async def retrieve(doi: str = None, url: str = None):
    article_info = retrieve_article(doi=doi, url=url)
    if article_info in ["No DOI or URL provided.", "Article not found in database."]:
        raise HTTPException(status_code=404, detail=article_info)
    return article_info


@app.get("/search/")
async def search_papers(term: str, sort: str = "new_to_old"):
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    order = "DESC" if sort == "new_to_old" else "ASC"
    query = f"""SELECT title, doi, date FROM articles
                WHERE keywords LIKE '%' || ? || '%'
                OR model_metadata LIKE '%' || ? || '%'
                ORDER BY date {order}"""
    c.execute(query, (term, term,))
    results = c.fetchall()
    conn.close()
    if results:
        return [{"title": result[0], "doi": result[1], "date": result[2]} for result in results]
    else:
        return []


