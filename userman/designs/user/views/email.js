/* Userman
   Index user documents by email.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    emit(doc.email, null);
}
