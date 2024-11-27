# Use the Node.js LTS image
FROM node:18 AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json for dependency installation
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the Next.js app
RUN npm run build

# Production image
FROM node:18

# Set the working directory
WORKDIR /app

# Copy only the build and necessary files from the builder
COPY --from=builder /app/package.json /app/package-lock.json /app/
COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public

# Install production dependencies
RUN npm install --production

# Expose the default Next.js port
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "start"]
