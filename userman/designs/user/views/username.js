/* Userman
   Index user documents by username.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    if (doc.username) emit(doc.username, null);
}
