import os
import json
import re
from lxml import etree
from nltk.stem import SnowballStemmer
from functools import reduce


class Indice:
    _INDICE_MEDIOS = {"1": "telam", "2": "clarin", "3": "lavoz", "4": "lanacion", "5": "perfil"}
    _INDICE_SECCION = {"1": "economia", "2": "mundo", "3": "politica", "4": "sociedad", "5": "ultimas"}
    _INDICE_ELEMENTO = {"1": "titulo", "2": "descripcion"}
    _WORD_MIN_LENGTH = 3
    _STOP_WORDS = frozenset(['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los',
                             'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es',
                             'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 'sí',
                             'porque', 'esta', 'son', 'entre', 'está', 'cuando', 'muy', 'sin', 'sobre',
                             'ser', 'tiene', 'también', 'me', 'hasta', 'hay', 'donde', 'han', 'quien',
                             'están', 'estado', 'desde', 'todo', 'nos', 'durante', 'estados', 'todos',
                             'uno', 'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'había',
                             'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo',
                             'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes',
                             'nada', 'muchos', 'cual', 'sea', 'poco', 'ella', 'estar', 'haber', 'estas',
                             'estaba', 'estamos', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te',
                             'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío',
                             'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya',
                             'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro',
                             'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás', 'está',
                             'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 'estén',
                             'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría',
                             'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas',
                             'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo',
                             'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras',
                             'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses',
                             'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada',
                             'estados', 'estadas', 'estad', 'none', 'he', 'has', 'ha', 'hemos', 'habéis', 'han',
                             'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá',
                             'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais',
                             'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube',
                             'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras',
                             'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos',
                             'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas',
                             'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis',
                             'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería',
                             'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais',
                             'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera',
                             'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos',
                             'fueseis', 'fuesen', 'siendo', 'sido', 'sed', 'tengo', 'tienes', 'tiene',
                             'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 'tengáis',
                             'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos', 'tendréis', 'tendrán',
                             'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía',
                             'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo',
                             'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos',
                             'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis',
                             'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened', ''])

    def formar_indice(self):
        """Actualiza el indice, en caso de que no exista lo crea"""
        basic_path = os.path.join(os.path.dirname(__file__), "..", "Indice")
        try:
            diccionario = json.load(open(os.path.join(basic_path, "Dic.json")))
        except:
            diccionario = {"1": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "2": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "3": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "4": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                           "5": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}}
        self.SPIMI(diccionario, basic_path)
        json.dump(diccionario, open(os.path.abspath(os.path.join(basic_path, "Dic.json")), "w"))
        self.merge(basic_path, 4)

    def SPIMI(self, diccionario, basic_path):
        """
        SPIMI : Single-pass in-memory indexing
        crea multiples archivos intermedios con termino : postings
        :param diccionario: con los indices de los ultimos elementos agregados al indice
        :return:
        """
        for medio in diccionario.keys():
            indice = {}
            for seccion in sorted(diccionario[medio].keys()):
                noticias = self.obtener_noticias((medio, seccion, diccionario[medio]), basic_path)
                noticias = list(map(
                    lambda x: (self.normalizar_string(x[0]), self.normalizar_string(x[1]), diccionario[medio][seccion]),
                    noticias))
                for titulo, descripcion, id_noticia in noticias:
                    for word in titulo:
                        indice.setdefault(word, []).append(
                            (medio + str((int(seccion) * 2) - 2) + '{0:03d}'.format(id_noticia)))
                for titulo, descripcion, id_noticia in noticias:
                    for word in descripcion:
                        indice.setdefault(word, []).append(
                            (medio + str((int(seccion) * 2) - 1) + '{0:03d}'.format(id_noticia)))
            temp = open(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'wt')
            for termino in sorted(indice.keys()):
                temp.write(termino + ';' + ''.join([str(x) + ',' for x in indice[termino]])[:-1] + "\n")
            temp.close()

    def obtener_noticias(self, posicion, basic_path):
        """
        :param posicion: tupla con medio, seccion, diccionario con id noticia anterior
        :return: todas las noticias de un medio y seccion especificas a partir de un id
        """
        tree = etree.parse(os.path.join(basic_path, "..", "sources", self._INDICE_MEDIOS[posicion[0]] + ".xml"),
                           etree.XMLParser(remove_blank_text=True))
        noticia_str = "seccion[" + posicion[1] + "]/noticia[" + str(posicion[2][posicion[1]] + 1) + "]"
        if len(tree.xpath(noticia_str)) == 0:
            return
        posicion[2][posicion[1]] += 1
        yield tree.xpath(noticia_str + "/titulo")[0].text, tree.xpath(noticia_str + "/descripcion")[0].text
        for noticia in tree.xpath(noticia_str)[0].itersiblings():
            posicion[2][posicion[1]] += 1
            yield (noticia.xpath("titulo")[0].text, noticia.xpath("descripcion")[0].text)

    def normalizar_string(self, str):
        """ :return: lista de palabras normalizadas"""
        stemmer = SnowballStemmer('spanish')
        str = re.split(r"[0-9_\W]", str)
        words = []
        for word in str:
            if word != "" and word not in self._STOP_WORDS and len(word) >= self._WORD_MIN_LENGTH:
                words.append(stemmer.stem(word))
        return words

    def merge(self, basic_path, block_size):
        """
        Unifica los archivos intermedios creados por SPIMI en un indice comprimido que consiste en un "block storage"
        con las palabras y una estructura auxiliar con los postings y referencias al "block storage"
        :param basic_path: path de la carpeta Indice donde se encuentras los archivos
        :param block_size: tamaño de cada bloque en el "block storage"
        """
        intermedios = []
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            intermedios.append(open(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'), 'rt'))
        lineas = []
        block_storage = open(os.path.join(basic_path, "block_storage" + '.txt'), 'wt')
        estructura_auxiliar = open(os.path.join(basic_path, "estructura_auxiliar" + '.txt'), 'wt')
        for archivo in intermedios:
            lineas.append(archivo.readline().split(";"))
        indice = 0
        postings = []
        salto = 0
        while lineas:
            palabra = lineas[0][0]
            apariciones = []
            for x in range(0, len(lineas)):
                if lineas[x][0] < palabra:
                    palabra = lineas[x][0]
                    apariciones = [x]
                elif lineas[x][0] == palabra:
                    apariciones.append(x)
            resultado = ""
            for i in apariciones:
                resultado += lineas[i][1][:-1] + ","
                lineas[i] = intermedios[i].readline().split(";")
                if len(lineas[i][0]) == 0:
                    intermedios[i].close()
                    del (intermedios[i])
                    del (lineas[i])
                    for i in range(0, len(apariciones)):
                        apariciones[i] -= 1
            jump = len(palabra)
            block_storage.write(str(jump) + palabra)
            postings.append(resultado[:-1])
            if len(postings) == block_size:
                estructura_auxiliar.write(str(indice) + "-" + self.comprimir_postings(postings) + ";")
                postings = []
                indice += salto
                salto = 0
            salto += len(str(jump)) + jump
        if len(postings) != 0:
            estructura_auxiliar.write(str(indice) + "-" + self.comprimir_postings(postings) + ";")
        estructura_auxiliar.close()
        block_storage.close()
        for medio in sorted(self._INDICE_MEDIOS.keys()):
            os.remove(os.path.join(basic_path, 'spimi' + self._INDICE_MEDIOS[medio] + '.txt'))

    def comprimir_postings(self, postings):
        """
        :param postings: string con los postings
        :return: string comprimido con los postings
        """
        res = ""
        for post in postings:
            elementos = post.split(",")
            res += elementos[0]
            for i in range(len(elementos) - 1, 0, -1):
                elementos[i] = str(int(elementos[i]) - int(elementos[i - 1]))
            for i in range(1, len(elementos)):
                res += "+" + elementos[i]
            res += ","
        return res[:-1]

    def obtener_apariciones(self, palabra):
        """Devuelve un SET con las apariciones de la palabra"""
        pass

    def obtener_todos_docs(self):
        """Devuelve un SET con todos los docs"""
        pass


# Test creacion-actualizacion indice
if __name__ == '__main__':
    Indice().formar_indice()