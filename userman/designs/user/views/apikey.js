/* Userman
   Index user documents by API key.
   Value: email.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    emit(doc.apikey, doc.email;
}
