FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./conf.d/default.conf /etc/nginx/conf.d/

# Раскомментируйте, если есть статика:
# COPY ./static /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]