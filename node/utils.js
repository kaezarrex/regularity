
/**
 * Add the number of milliseconds to the date.
 * @param date : Date
 *     the date to add to
 * @param ms : int
 *     the number of milliseconds to add
 */
function dateAdd(date, ms) {
    return new Date(date.getTime() + ms);
}

exports.dateAdd = dateAdd;

