import { Module, Controller, Post, Get, Body, Req, Res, UnauthorizedException } from '@nestjs/common';
import { Request, Response } from 'express';
import { db } from '../db';

@Controller('api/auth')
export class AuthController {
  
  @Post('login')
  login(@Body() body: any, @Res({ passthrough: true }) res: Response) {
    const { username, password } = body;
    const user = db.users.find(u => u.username === username && u.password === password);
    
    if (user) {
      res.cookie('session_id', user.id.toString(), { httpOnly: true, sameSite: 'lax' });
      return { success: true, user: { username: user.username, role: user.role } };
    }
    throw new UnauthorizedException('Invalid credentials');
  }

  @Post('logout')
  logout(@Res({ passthrough: true }) res: Response) {
    res.clearCookie('session_id');
    return { success: true };
  }

  @Get('me')
  getMe(@Req() req: Request) {
    const sessionId = req.cookies['session_id'];
    if (!sessionId) {
      throw new UnauthorizedException('Unauthenticated');
    }
    const user = db.users.find(u => u.id.toString() === sessionId);
    if (user) {
      return { username: user.username, role: user.role };
    }
    throw new UnauthorizedException('Unauthenticated');
  }
}

@Module({
  controllers: [AuthController],
})
export class AuthModule {}
