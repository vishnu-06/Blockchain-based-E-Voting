# Blockchain-based-E-voting
In our project, we will be demonstrating the use of Parallel mining and the distributed nature of Blockchain through a secure voting website. On the voting website, the users get to vote in a secure manner by using the properties of the blockchain. Whenever a user casts his/her vote the transaction is added to a block, based on timestamp. At the same time, this transaction is stored on multiple distributed remote databases. This block is then mined at the server side while counting the votes. Here we use game theory to generate nonce value in an inefficient and faster way using multiple threads with the help of parallel mining.

## Architecture Diagram
![image](https://user-images.githubusercontent.com/70327869/196694443-5a8b90fd-3479-4c84-8af1-96ae803268d0.png)

## Screenshots

**Landing Page**
![image](https://user-images.githubusercontent.com/70327869/196695094-7a0c7acb-8826-4bc6-b1ad-fb3360f6e755.png)

**Candidate selection and Voting Page**
![image](https://user-images.githubusercontent.com/70327869/196695172-f0f868b9-5856-4112-b38b-bf9d754f9a7e.png)

**Generating votes and Mining into Blocks**
![image](https://user-images.githubusercontent.com/70327869/196695279-12355f46-eff1-4d3c-90cc-0982136ce187.png)

**Mined Blocks and Details**
![image](https://user-images.githubusercontent.com/70327869/196695346-41aa5dad-36dd-4122-81c8-7635553ec68f.png)

**Voter Data (Confirmed Transactions in Block)**
![image](https://user-images.githubusercontent.com/70327869/196695545-bbd66da6-a445-4d0d-a737-e8fb7ef071c5.png)

## Result
**Performance Chart (Blockchain difficulty vs Mining Time for n processes)**
![image](https://user-images.githubusercontent.com/70327869/196695763-db447b74-79e4-45a4-9bc5-bb88abeea9f3.png)


