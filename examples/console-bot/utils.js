module.exports = {

    showOptions: function(text) {
        var textosFiltro = [];
        var useEntities = false;
        textosFiltro.push('No se de que me hablas');
        textosFiltro.push('No lo se');
        textosFiltro.push('Ese tipo de cosas estan lejos de mi campo de conocimiento');
        textosFiltro.push('No entiendo tu pregunta. Prueba a reformularla');
        textosFiltro.push('No he entendido tu pregunta. Prueba otra vez');
        textosFiltro.push('Lo siento, no te he entendido');

        if (textosFiltro.includes(text)) {
            useEntities = true;
            return useEntities;
        }

    },

    entitiesInfo: function(entity, option) {
        var response = "";
        response += "**************";

        return response;
    }
}