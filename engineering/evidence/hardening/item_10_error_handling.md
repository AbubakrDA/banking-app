# Item 10 Plan — Error Envelope & Specific 4xx Mapping

## Plan
- Update `backend/app/main.py`:
  - Safe serialization in `validation_exception_handler` (`422 VALIDATION_ERROR`).
  - Map `ValueError` to specific 4xx codes (`404 NOT_FOUND`, `403 FORBIDDEN`, `409 CONFLICT`, `400 BAD_REQUEST`) in `APIResponse.fail`.
  - Add `unhandled_exception_handler` returning sanitized `500 INTERNAL_SERVER_ERROR` `APIResponse.fail` without stack traces or internal error messages.
- Test 404, 422, `ValueError` 4xx mapping, and 500 sanitization in `backend/tests/test_api_error_envelopes.py`.

## Evidence
```
$ python -m pytest tests/test_api_error_envelopes.py tests/test_health.py -v
5 passed in 0.48s
```
- **Status:** `VERIFIED`
