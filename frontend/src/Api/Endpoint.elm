module Api.Endpoint exposing (..)

import Http
import Url.Builder



{-| Get a URL to the Conduit API.

This is not publicly exposed, because we want to make sure the only way to get one of these URLs is from this module.

-}
type Endpoint
    = Endpoint String


unwrap : Endpoint -> String
unwrap (Endpoint str) =
    str


url : List String -> Endpoint
url paths =
    -- NOTE: Url.Builder takes care of percent-encoding special URL characters.
    -- See https://package.elm-lang.org/packages/elm/url/latest/Url#percentEncode
    Url.Builder.absolute
        paths []
        |> Endpoint



-- ENDPOINTS


entries : Endpoint
entries =
    url [ "entries" ]

reload : Endpoint
reload =
    url [ "reload" ]


