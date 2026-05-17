import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { Request } from 'express';
import { db } from '../db';

@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<Request>();
    const sessionId = request.cookies['session_id'];
    
    if (!sessionId) {
      throw new UnauthorizedException('Authentication required');
    }
    
    const user = db.users.find(u => u.id.toString() === sessionId);
    if (!user) {
      throw new UnauthorizedException('Invalid session');
    }
    
    // Attach user to request
    request['user'] = user;
    return true;
  }
}
