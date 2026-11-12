JWT_SECRET_KEY = "c6ecd2b8-4109-4cbe-aff3-fadb502ff77e"
JWT_ALOGO = "HS256"
JWT_ISSUER = "http://localhost:8001"
JWT_EXPIRE_HOURS = 1
JWT_AUDIENCE = "my-mcp-server"


from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

verifer = JWTVerifier(
    public_key=JWT_SECRET_KEY,
    algorithm=JWT_ALOGO,
    issuer=JWT_ISSUER,
    audience=JWT_AUDIENCE
)

mcp = FastMCP("Secure MCP Server", auth = verifer)

@mcp.tool
def whoami() -> dict:
    """
        This tool will return the user information based on the JWT token provided in the request header.
    """
    token = get_access_token()
    print("\n\n", token, "\n\n")
    return {
        "client_id": token.client_id
    }

mcp.run(transport = "streamable-http")