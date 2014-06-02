/* Userman
   Index user documents by role.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    emit(doc.role, null);
}
