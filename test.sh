#!/bin/bash

export API_KEY=WY7jk10L.o9jEPKlv.jYlCwL3X0vDVduNJ5Z8bzSpc

for i in 1 2 3 4; do
  curl -s -o /dev/null -D - -H "X-Api-Key: $API_KEY" \
    http://127.0.0.1:8000/listas_de_acuerdos/visualizar/153226 | grep -iE "^HTTP|retry-after"
done
