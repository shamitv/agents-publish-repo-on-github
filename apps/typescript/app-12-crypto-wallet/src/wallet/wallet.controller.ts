import { Controller, Get, Post, Body, UseGuards, Req } from '@nestjs/common';
import { WalletService } from './wallet.service';
import { AuthGuard } from '../auth/auth.guard';
import { Request } from 'express';

@Controller('api/wallet')
@UseGuards(AuthGuard)
export class WalletController {
  constructor(private readonly walletService: WalletService) {}

  @Get()
  getWallet(@Req() req: Request) {
    const user = req['user'];
    return this.walletService.getWallet(user.id);
  }

  @Get('transactions')
  getTransactions(@Req() req: Request) {
    const user = req['user'];
    const wallet = this.walletService.getWallet(user.id);
    return this.walletService.getTransactions(wallet.address);
  }

  // OWASP A04: Insecure Design. No transaction confirmation step.
  // The transfer executes immediately without intent verification (e.g. CSRF token, confirmation prompt).
  @Post('transfer')
  transferFunds(@Req() req: Request, @Body() body: { recipientAddress: string; amount: number }) {
    const user = req['user'];
    return this.walletService.executeTransfer(user.id, body.recipientAddress, body.amount);
  }
}
