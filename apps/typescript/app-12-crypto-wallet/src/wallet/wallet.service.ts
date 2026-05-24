import { Injectable, BadRequestException } from '@nestjs/common';
import { db } from '../db';
@Injectable()
export class WalletService {
  getWallet(userId: number) {
    const wallet = db.wallets.find(w => w.userId === userId);
    if (!wallet) {
      throw new BadRequestException('Wallet not found');
    }
    return wallet; 
  }
  getTransactions(address: string) {
    return db.transactions.filter(t => t.sender === address || t.receiver === address);
  }
  executeTransfer(userId: number, recipientAddress: string, amount: number) {
    if (amount <= 0) {
      throw new BadRequestException('Transfer amount must be positive');
    }
    const senderWallet = db.wallets.find(w => w.userId === userId);
    if (!senderWallet) {
      throw new BadRequestException('Sender wallet not found');
    }
    if (senderWallet.address === recipientAddress) {
      throw new BadRequestException('Cannot transfer to self');
    }
    if (senderWallet.balance < amount) {
      throw new BadRequestException('Insufficient balance');
    }
    const recipientWallet = db.wallets.find(w => w.address === recipientAddress);
    if (!recipientWallet) {
      throw new BadRequestException('Recipient address not found');
    }
    // Process transfer atomically
    senderWallet.balance -= amount;
    recipientWallet.balance += amount;
    const transaction = {
      id: db.transactions.length + 1,
      sender: senderWallet.address,
      receiver: recipientWallet.address,
      amount,
      timestamp: new Date().toISOString()
    };
    db.transactions.push(transaction);
    return {
      success: true,
      transaction,
      newBalance: senderWallet.balance
    };
  }
    if (amount <= 0) {
      throw new BadRequestException('Transfer amount must be positive');
    }
    const senderWallet = db.wallets.find(w => w.address === fromAddress);
    if (!senderWallet) {
      throw new BadRequestException('Source wallet not found');
    }
    if (fromAddress === toAddress) {
      throw new BadRequestException('Cannot transfer to self');
    }
    if (senderWallet.balance < amount) {
      throw new BadRequestException('Insufficient balance');
    }
    const recipientWallet = db.wallets.find(w => w.address === toAddress);
    if (!recipientWallet) {
      throw new BadRequestException('Recipient address not found');
    }
    senderWallet.balance -= amount;
    recipientWallet.balance += amount;
    const transaction = {
      id: db.transactions.length + 1,
      sender: fromAddress,
      receiver: toAddress,
      amount,
      timestamp: new Date().toISOString()
    };
    db.transactions.push(transaction);
    return { success: true, transaction, newBalance: senderWallet.balance };
  }
}
