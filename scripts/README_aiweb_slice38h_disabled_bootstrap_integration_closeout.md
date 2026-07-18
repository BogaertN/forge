# Slice 38H Operator Notes

Slice 38H is a disabled integration and closeout slice.  It does not add a
public route or production capability.

The operator workflow is:

1. Verify the external patch checksum.
2. Verify the package and protected predecessor hashes.
3. Apply the exact payload to a clean repository at the accepted Slice 38G
   parent.
4. Run all tests visibly and sequentially.
5. Preserve the generated result archive and checksum.
6. Upload the result archive and checksum for independent review.
7. Stage and commit only after that review and separate authorization.
8. Do not push without separate explicit authorization.

The default integration state refuses execution.  An enabled run accepts only
one exact synthetic fixture identity and carries no raw text.  All output is
candidate-only or explicit non-progress.
