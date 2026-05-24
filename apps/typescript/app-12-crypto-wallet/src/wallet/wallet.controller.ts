import { Controller, Get, Post, Body, UseGuards, Req, Query } from '@nestjs/common';
import { WalletService } from './wallet.service';
import { AuthGuard } from '../auth/auth.guard';
import { Request } from 'express';
@Controller('api/wallet')
@UseGuards(AuthGuard)
export class WalletController {
  constructor(private readonly walletService: WalletService) {}
  // it matches the authenticated user. Any authenticated wallet holder can view any
  // other user's wallet by supplying their userId, including their private key.
  @Get()
  getWallet(@Req() req: Request, @Query('userId') userId?: string) {
    const user = req['user'];
    const targetUserId = userId ? parseInt(userId, 10) : user.id;
    return this.walletService.getWallet(targetUserId);
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
  // without verifying the authenticated user owns that address. An attacker who obtained
  // a victim's wallet address via the IDOR endpoint in step 1 can transfer funds out of
  // the victim's wallet without possessing the private key.
  @Post('external-transfer')
  externalTransfer(
    @Req() req: Request,
    @Body() body: { fromAddress: string; toAddress: string; amount: number },
  ) {
    // Vulnerable: no ownership check — fromAddress not verified against req['user']
    return this.walletService.executeTransferByAddress(body.fromAddress, body.toAddress, body.amount);
  }
}