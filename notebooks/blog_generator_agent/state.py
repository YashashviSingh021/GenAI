from pydantic import BaseModel

class BlogState(BaseModel):
    ###user input
    topic: str = ""
    audience: str = ""

    ###researcher output
    research: str = ""
    research_feedback: str = ""

    ##writer output
    draft: str = ""
    draft_feedback: str = ""

    ###Editor Output
    final_blog: str = ""

    ### Metadata
    revision_count: int = 0