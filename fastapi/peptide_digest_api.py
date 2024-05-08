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


def retrieve_article(doi=None, url=None, pii=None):
    """
    Retrieve an article from a SQLite database.

    Parameters
    ----------
    doi : str, optional
        The DOI of the article to be retrieved.
    url : str, optional
        The URL of the article to be retrieved.
    pii : str, optional
        The PII of the article to be retrieved.

    Returns
    -------
    dict
        A dictionary containing the title, authors, journal, date, URL, DOI, and keywords of the article.
    """
    if not doi and not url and not pii:
        return "No article identifier provided."

    if url and not url.startswith("https://"):
        if url.startswith("www."):
            url = "https://" + url
        else:
            url = "https://www." + url

    conn = sqlite3.connect("../data/articles.db")
    c = conn.cursor()

    if doi:
        c.execute(
            """SELECT * FROM article_info WHERE doi = ?""",
            (doi,),
        )
        article_info = c.fetchone()

        c.execute(
            """SELECT * FROM model_responses WHERE doi = ?""",
            (doi,),
        )
        model_responses = c.fetchone()
    
    elif url:
        c.execute(
            """SELECT * FROM article_info WHERE url = ?""",
            (url,),
        )
        article_info = c.fetchone()

        c.execute(
            """SELECT * FROM model_responses WHERE url = ?""",
            (url,),
        )
        model_responses = c.fetchone()
    
    elif pii:
        pii = "https://www.sciencedirect.com/science/article/pii/" + pii
        c.execute(
            """SELECT * FROM article_info WHERE url = ?""",
            (pii,),
        )
        article_info = c.fetchone()

        c.execute(
            """SELECT * FROM model_responses WHERE url = ?""",
            (pii,),
        )
        model_responses = c.fetchone()
    else:
        return "No article identifier provided."
    conn.close()

    if article_info and model_responses:
        article_result = {
            "title": article_info[1],
            "authors": article_info[2],
            "journal": article_info[3],
            "publisher": article_info[4],
            "date": article_info[5],
            "url": article_info[6],
            "doi": article_info[7],
            "keywords": article_info[8],
            "scidir/pmc": article_info[9],  
            "pmc_id": article_info[10],  
            "bullet_points": model_responses[2],
            "summary": model_responses[3],
            "metadata": model_responses[4],
            "score": model_responses[5],
            "score_justification": model_responses[6]
        }

        return article_result
    else:
        return "Article not found in database."


@app.get("/retrieve/")
async def retrieve(doi: str = None, url: str = None, pii: str = None):
    article_info = retrieve_article(doi=doi, url=url, pii=pii)
    if article_info in [
        "No article identifier provided.",
        "Article not found in database.",
    ]:
        raise HTTPException(status_code=404, detail=article_info)
    return article_info


@app.get("/search/")
async def search_papers(term: str, sort: str = "new_to_old"):
    conn = sqlite3.connect("../data/articles.db")
    c = conn.cursor()

    # Determine the ORDER BY clause based on the sort parameter
    if sort == "score":
        order_by_clause = "model_responses.score DESC"
    else:
        # Default to sorting by date
        order_by_clause = "article_info.date DESC" if sort == "new_to_old" else "article_info.date ASC"

    query = f"""SELECT article_info.title, article_info.doi, article_info.date, model_responses.score 
                FROM article_info
                LEFT JOIN model_responses ON article_info.doi = model_responses.doi
                WHERE article_info.keywords LIKE '%' || ? || '%'
                OR model_responses.metadata LIKE '%' || ? || '%'
                ORDER BY {order_by_clause}"""
    c.execute(
        query,
        (
            term,
            term,
        ),
    )
    results = c.fetchall()
    conn.close()

    if results:
        return [
            {
                "title": result[0],
                "doi": result[1],
                "date": result[2],
                "score": result[3],
            }
            for result in results
        ]
    else:
        return []