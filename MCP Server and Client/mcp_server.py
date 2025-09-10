from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

# MCP package used to create MCP server
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# MCP SDKs helps define tools 
# Example tool definition and handling 

# @mcp.tool(
#     name="add_ints",
#     description="Add two integers together"
# )

# def tool_fn(
#     a = Field(description="First number to add"),
#     b = Field(description="Second numver to add"),
# ) -> int:
#     return a + b

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_doc",
    description="Read contents of the document and return it as a string"
)

def read_doc(
    doc_id: str = Field(description="ID of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with ID {doc_id} not found")
    
    return docs[doc_id]


@mcp.tool(
    name="edit_doc",
    description="Edit a document by replacing a string in the documents context with the provided alternative"
)

def edit_doc(
    doc_id:str = Field(description="ID of the document that will be edited"),
    old_str: str = Field(description="Text to replace must match exactly including white space"),
    new_str: str = Field(description="New text to inseert in place of old text")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with ID {doc_id} not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

# TODO: Write a resource to return all doc id's
@mcp.resource(
    "docs://documents",  # URI for accessing the document ID
    mime_type="application/json"  # Hinting the client on what type of data is returned.
)

def list_docs() -> list[str]:
    return list(docs.keys)  # Python SDK will take whatever we are sending and turn it into a list for us

# TODO: Write a resource to return the contents of a particular doc

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)

def fetch_doc(doc_id: str) -> str: 
    if doc_id not in docs:
        raise ValueError(f"Doc with ID {doc_id} is not found")
    
    return docs[doc_id]

@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in markdown format"
)

def format_doc(
    doc_id: str=Field(description="ID of the document to format")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The ID of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables etc as necessary. Feel free to add in structure.
    Use the 'edit_document' tool to edit the document. After the document has been reformatted...
    """

    return [
        base.UserMessage(prompt)
    ]

# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
