FROM node:18.2.0

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install --silent
RUN npm install react-scripts@3.4.1 -g --silent

# add app
COPY public ./public
COPY src ./src

# Update version file
ARG APP_VERSION
RUN echo "{\"version\": \"$APP_VERSION\"}" > src/meta/version.json

EXPOSE 3000

COPY ./entrypoint.sh /entrypoint.sh

# start app
ENTRYPOINT ["bash", "/entrypoint.sh"]
CMD ["npm", "start"]
