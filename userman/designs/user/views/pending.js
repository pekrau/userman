/* Userman
   Index user documents that are in status 'pending'.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    if (doc.status === 'pending') emit(doc.modified, null);
}
