module Api exposing (..)

{-| This module is responsible for communicating to the Conduit API.

It exposes an opaque Endpoint type which is guaranteed to point to the correct URL.

-}

import Api.Endpoint as Endpoint exposing (Endpoint)
import Http exposing (Body, Expect)
import Json.Decode as Decode exposing (Decoder, Value, decodeString, field, string)
import Json.Encode as Encode
import Url exposing (Url)
import String
import Http
import Json.Decode as D

import Api.Endpoint as EP -- exposing (unwrap, register)



get : Endpoint -> (Result String a -> msg) -> Decoder a -> Cmd msg
get url toMsg decoder =
    Http.request
        { method = "GET"
        , url = EP.unwrap url
        , expect = genericExpectJson toMsg decoder
        , headers = []
        , body =  Http.emptyBody
        , timeout = Nothing
        , tracker = Nothing
        }


post : Endpoint -> Body -> (Result String a -> msg) -> Decoder a -> Cmd msg
post url body toMsg decoder =
    Http.request
        { method = "POST"
        , url = EP.unwrap url
        , expect = genericExpectJson toMsg decoder
        , headers = []
        , body =  body
        , timeout = Nothing
        , tracker = Nothing
        }



genericExpectJson : (Result String a -> msg) -> D.Decoder a -> Expect msg
genericExpectJson toMsg decodeRes =
  Http.expectStringResponse toMsg <|
    \response ->
      case response of
        Http.BadUrl_ url ->
          Err ("Bad Url: " ++ url)

        Http.Timeout_ ->
          Err ("Time out")

        Http.NetworkError_ ->
          Err ("Network error")

        Http.BadStatus_ metadata body -> Err ("Bad status: " ++ String.fromInt metadata.statusCode)

        Http.GoodStatus_ metadata body ->
          case D.decodeString decodeRes body of
            Ok value ->
              Ok value

            Err err ->
              Err ("Bad Body: " ++ D.errorToString err)



entries toMsg =
  get EP.entries toMsg

reload =
  get EP.reload

