module.exports = async function entitiesnlp(EntityManager) {

    const entity = EntityManager.addNamedEntity('email', 'regex');
    entity.addRegex('en', /\b(\w[-._\w]*\w@\w[-._\w]*\w\.\w{2,3})\b/gi);
}