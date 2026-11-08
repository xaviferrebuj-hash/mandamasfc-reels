# Mandamás FC · fábrica de vídeos para redes

Repositorio **público**: aquí solo entra material publicable (vídeos ya aprobados, sus textos y el script de montaje). Nada de claves, código del juego, datos de jugadores ni capturas con datos.

## Flujo
| Paso | Quién | Estado de la pieza |
|---|---|---|
| Claude prepara el lote de la semana (vídeo + textos) | Claude | `preparado` |
| Xavi lo ve y da el OK | Xavi | `aprobado` |
| El vídeo se sube aquí y se programa en Metricool (Instagram, TikTok y YouTube Shorts) | Claude | `programado` |
| Se comprueba en Metricool que ha salido | Claude | `publicado` |

«Aprobado» no es programado, y «programado» no es publicado: el estado se confirma leyendo Metricool.

## Reglas
- Solo el Atlético Bastión y rivales inventados; nunca nombres ni escudos reales.
- Si el vídeo lleva viñetas hechas con IA: marcado como IA en TikTok y YouTube.
- Enlaces con su etiqueta: `mandamasfc.com/ig`, `/tiktok`, `/yt` (+ `?utm_campaign=<slug>`).
- MP4 1080×1920, 30 fps, H.264 + AAC, −14 LUFS, ≤ 9,5 MB.

## Montaje
`python3 fabrica/montar.py pieza.json salida.mp4` (Pillow + ffmpeg). Fuentes: Bebas Neue y Source Sans 3 (SIL Open Font License).
