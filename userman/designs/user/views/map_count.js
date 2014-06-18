/* Userman
   Index user documents by status.
   Value: 1.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    if (!doc.status) return;
    emit(doc.status, 1);
}
