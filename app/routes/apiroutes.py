from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app.auth.crypt import isUser, validateCsrf, validatePassword
from app.auth.session import isAuthenticated

# form validation
from app.models.verify import LoginForm

router = APIRouter()


@router.post("/login", response_class=HTMLResponse)
async def loginForm(
    request: Request, data: Annotated[LoginForm, Form()]
) -> RedirectResponse:
    """POST API endpoint for login attempts

    Args:
        request (Request): The request object describing the app and client
        data (Annotated[LoginForm, Form]): The form the user filled in

    Returns:
        Error (HTTPException):
            If the user is already logged in, he should not be sending any message,
            so a code 400 is raised and sent

        Home (Redirect):
            If the user provides correct credentials, matches the CSRF token,
            and is not logged in, they are redirected to "home" and we remember
            that the user is logged in.

        Login (RedirectResponse):
            If the user does not provide correct credentials, they are sent back to
            home and we update the errors with the login attempt.
    """
    # we should not even consider this if the user is already logged in
    if isAuthenticated(request):
        # 303 code because we are on a POST endpoint
        raise HTTPException(status_code=400, detail="Already logged in.")

    # first clear existing errors
    request.session["errors"] = None
    # first we check if the csrf tokens are correct
    errors: dict[str, str] = {}

    if not validateCsrf(request, data.csrf):
        errors["csrf"] = "Invalid session. Try login again."

    if not isUser(data.username):
        errors["username"] = "Username does not exist"
    elif not validatePassword(data.username, data.password):
        errors["password"] = "Password is not correct!"

    if errors:
        request.session["errors"] = errors
        return RedirectResponse(request.url_for("login"), status_code=303)

    print("Login OK!")
    request.session["user"] = data.username
    return RedirectResponse(url=request.url_for("home"), status_code=303)


@router.post("/logout")
def logout(request: Request, csrf: Annotated[str, Form()]) -> RedirectResponse:
    """POST API endpoint for logout attempts

    Args:
        request (Request): The request object describing the app and client
        csrf (Annotated[str, Form]): A hidden form containing the CSRF token

    Returns:
        Home (HTTPException):
            If the user does not provide a valid CSRF token, we send back a 400 error
        Login (RedirectResponse)
            If the user provides the correct CSRF token, they are redirected to /login
    """
    # if the CSRF token is incorrect -> untrusted request
    if not validateCsrf(request, csrf):
        raise HTTPException(400, "CSRF token incorrect, operation not allowed.")
    # if it is correct -> we clear everything
    request.session.clear()
    return RedirectResponse(url=request.url_for("login"), status_code=303)


# to allow anyone to see the icon, not that important
@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """favicon

    Using this explicit endpoint allows us to specify and acess the favicon anywhere.

    Returns:
        favicon (FileResponse): the favicon.ico file
    """
    return FileResponse("static/favicon.ico")
