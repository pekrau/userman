/* Userman
   Index user documents that are in status 'blocked'.
   Value: null.
*/
function(doc) {
    if (doc.userman_doctype !== 'user') return;
    if (doc.status === 'blocked') emit(doc.modified, null);
}
